# -*- coding: utf-8 -*-

import sys
import os
import re
import json
import base64
import requests
import string
import ftplib
import threading
import time
from datetime import datetime
import skypebot
import urllib
import sched
import subprocess
import shutil
import traceback
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.file_message import FileMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest

from flask import Flask, request, Response, send_from_directory 

app = Flask(__name__)
skypedata =[["zzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzz","zzzzzzzzzzzzzzzzzz"],
    ["zzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzz","zzzzzzzzzzzzzzzzzz"],
    ["zzzzzz-zzzz-zzzz-zzzz-zzzzzzzzzzz","zzzzzzzzzzzzzzzzzz"]]

auth_token_viber='zzzzzzzzzzzzzz-zzzzzzzzzzzzz-zzzzzzzzzzzzzzz'
ftproot = "C:\\Inetpub\\ftproot\\"
website = 'https://magnitcloud.by'
pathbot = 'c:\\inetpub\\wwwroot\\bot\\'
sleeptime = 6

def writelog(msg, type = ""):
    f = open("log.txt", mode="a")
    f.write("{0} {1} {2}\n".format(type,time.ctime(),msg))
    f.close()
    
viber = Api(BotConfiguration(
  name='testbotnew',
  avatar='http://viber.com/avatar.jpg',
  auth_token=auth_token_viber
))

service_ ='https://smba.trafficmanager.net/apis/'
bot = []
for dat in skypedata:
    bot.append(skypebot.SkypeBot(dat[0],dat[1]))

def getTime():
    strs = ""
    dt = datetime.now()
    strs = strs + "{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}{:03d}".format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, int(dt.microsecond/1000))
    #writelog(strs)
    return strs
def getfiles(type_bot, indxbot = -1):
    try:
        pathsend = ftproot + type_bot+ "\\send\\"                 
        files = os.listdir(path=pathsend +".")
        files_pic = os.listdir(path=pathsend +"files\\.")
        for fn in files:               
            if fn.split('.')[-1] == 'txt' :
                #writelog(fn)
                f = open(pathsend+fn,'r')
                lines = []
                for line in f:
                    lines.append(line.rstrip())
                f.close()
                filesend = 0
                os.replace(pathsend+fn, pathsend+"sended\\"+fn)
                for fnp in files_pic:
                    fnp = fnp.replace("<file> ","")
                    
                    if fnp == lines[2]:
                        fnpencode = fnp.replace(" ","__")
                        #fnpencode = base64.b64encode(bytes(fnp, 'cp1251')).decode()
                        #writelog(fnpencode, type_bot)
                        if type_bot == 'viber':
                            #writelog(website+'/viber/' + fnpencode)    
                            viber.send_messages(lines[1], [
                                FileMessage(size=4096,media=website+'/files/viber/' + fnpencode, file_name=fnp)
                            ]) 
                        if indxbot != -1:
                            #writelog(website+'/skype/' + fnpencode)
                            ext = fnp.split('.')[-1] 
                            typefile = ''
                            if ext == 'jpg' or ext == 'png':
                                typefile = "image"
                                
                                bot[indxbot].send_media(service_, lines[1],typefile, website+'/files/'+type_bot+'/' + fnpencode)
                            else:
                                bot[indxbot].send_message(service_,lines[1],website+'/files/'+type_bot+'/' + fnpencode) 
                            
                        filesend = 1
                        break
                        
                if filesend == 0:   
                    indx = 0
                    messeges = ""
                    for i in lines:
                        if (indx >1):
                            messeges = messeges + i + '\n'
                        indx = indx + 1
                    writelog(messeges, type_bot)
                    if type_bot == 'viber':
                        try:
                            viber.send_messages(lines[1], [
                                TextMessage(None, None, messeges)
                            ])
                            #if(os.path.isfile(pathsend+fn)):
                            #    os.replace(pathsend+fn, pathsend+"sended\\"+fn)
                        except Exception as e:
                            pass
                    elif indxbot != -1:
                        bot[indxbot].send_message(service_,lines[1],messeges) 
                        #if(os.path.isfile(pathsend+fn)):
                        #    os.replace(pathsend+fn, pathsend+"sended\\"+fn)
               
            
    except Exception as e:
        writelog("{0}".format(traceback.format_exc()),type_bot) 
        pass


class ClockThread(threading.Thread):
    def __init__(self,interval):
        threading.Thread.__init__(self)
        self.daemon = True
        self.interval = interval
    def run(self):
        while True:
            time.sleep(self.interval)
            getfiles('skype', 0)
            k = 1
            while k < 10:
                getfiles('skype' + str(k), k)
                k = k + 1
            getfiles('viber')
            
               


def incomingViber(request):
    pathreceiveviber =  ftproot + "viber\\receive\\"   
    viber_request = viber.parse_request(request.get_data().decode("utf-8"))

    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
        typer = message.to_dict().get("type")
        fullname = pathreceiveviber + getTime() +".txt"
        if typer =="text":
            f = open(fullname, 'a')
            f.write(viber_request.sender.name+'\n'+viber_request.sender.id+'\n'+message.text+'\n') 
            f.close() 
        if typer =="file" or typer == "picture":
            urlf = message.to_dict().get("media")
            
            if typer == "file":
                namef =  getTime() +" " + message.to_dict().get("file_name")
            if typer == "picture":
                namef = getTime() + " " + viber_request.sender.name  +".jpg"
            #writelog(pathreceiveviber+ namef,"viber")
            try:
                response = requests.get(urlf, stream=True)
                with open(pathreceiveviber+'files\\' + namef, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response
                
                f = open(fullname, 'a')
                f.write(viber_request.sender.name+'\n'+viber_request.sender.id+'\n'+ "<file> "+namef+'\n') 
                f.close() 
            except Exception as e:
                writelog("{0}".format(traceback.format_exc()),"viber")
    return Response(status=200) 
    
def incomingSkype(data, indxbot):
    pathreceiveskype = ""
    if indxbot>0:
        pathreceiveskype =  ftproot + "skype" + str(indxbot)+"\\receive\\"
    else:
        pathreceiveskype =  ftproot + "skype\\receive\\"
    service = data['serviceUrl'] 
    try:
        if data['type'] =='conversationUpdate':
            sender = data['conversation']['id']
            if 'membersRemoved' in data.keys():
                left_member = data['recipient']['name']

            elif 'membersAdded' in data.keys():
                new_member = data['recipient']['name']
                
                bot[indxbot].send_message(service,sender,"Привет, я бот")
            else:
                pass
        elif data['type'] =='message':
        
            if 'isGroup' in data['conversation'].keys():
                sender = data['conversation']['id']
                if 'text' in data:
                    text = data['text'] 
                process_messages_skype(pathreceiveskype,sender,'group','time',text,service)
                
            else:
                sender = data.get('conversation').get('id')
                username = ''
                if 'from' in data and 'name' in data.get('from'):
                    username = data.get('from').get('name')
                time_s =  getTime()
                text = ''
            
                if 'text' in data:
                    text = data.get('text')
                    process_messages_skype(pathreceiveskype,sender,username, time_s, text,service)
                if 'attachments' in data:
                    try:
                        attachm = data.get('attachments')[0]
                        curl = attachm.get('contentUrl')
                        response = requests.get(curl, headers={"Authorization": "Bearer "+bot[indxbot].get_token(),"Content-Type":"application/json"},stream=True)
                        filen =  getTime()+" "+ attachm.get('name')
                        filename = pathreceiveskype +'files\\' + filen 
                        #writelog(filename,"skype")
                        with open(filename, 'wb') as out_file:
                            shutil.copyfileobj(response.raw, out_file)
                        del response
                        process_messages_skype(pathreceiveskype,sender,username, time_s, "<file> "+filen,service)
                    except Exception as e:
                        writelog("{0}".format(traceback.format_exc()),"skype")
        elif data['type'] == 'contactRelationUpdate':
        #bot added for private chat
        
            if data['action']=='add':
            
                sender = data['conversation']['id']
                bot[indxbot].send_message(service,sender,"Hi, I am a bot.")
                pass
            elif data['action']=='remove':
                pass
            else:
                pass
                
        else:
            pass                
    except Exception as e:
        writelog("{0}".format(traceback.format_exc()), "skype")                
      
@app.route('/files/<type>/<file>', methods=['GET'])
def retfile(type, file):
    try:
        file = file.replace("__"," ")
         
        #file = base64.b64decode(file).decode('cp1251')
        if type == 'viber' or type.find('skype')>-1:
            files_pic = os.listdir(path=ftproot + type +"\\send\\files\\.")
            if (file in files_pic):
                return send_from_directory(ftproot + type +"\\send\\files\\", file )
        
    except Exception as e:
        writelog("{0}".format(traceback.format_exc()),type)        
        
  
@app.route('/', methods=['POST','GET'])
def webhook_origin():
    
    if request.method == 'GET':
        return "bot"
    if request.method == 'POST':
        try:
            data = json.loads(request.data.decode('utf-8'))
            if 'serviceUrl' in data:
                writelog(request.data.decode('utf-8'),"skype")
                incomingSkype(data,0)
            else:
                writelog(request.data.decode('utf-8'),"viber")
                return incomingViber(request)
        except Exception as e:
            writelog("{0}".format(traceback.format_exc()))  

    return 'Ok'
@app.route('/<type>', methods=['POST','GET'])
def webhook(type):
    if type.find("skype")>-1:
        
        #writelog(request.method,type)
        if request.method == 'GET':
            return "bot "+type+ " "
        if request.method == 'POST':
            try:
                rdata = request.data.decode('utf-8')
                data = json.loads(rdata)
                writelog(rdata,"skype")
                incomingSkype(data,int(type[-1]))
            except Exception as e:
                writelog("{0}".format(traceback.format_exc()))  

    return 'Ok'

def process_messages_skype(path, sender,name, time, text,service):
    fullname = path + time +".txt"
    f = open(fullname, 'a')
    f.write(name+'\n'+sender+'\n'+text+'\n') 
    f.close() 
    
t = ClockThread(sleeptime)
t.start()   
        
if __name__ == '__main__': 
    app.run()