# -*- coding: utf-8 -*-

import sys
import os
import re
import json
import base64
import requests
import string
import threading
import time
from datetime import datetime
import skypebot
import subprocess
import shutil
import traceback
import logging
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

auth_token_viber='---'
ftproot = "C:\\Inetpub\\ftproot\\"
website = 'https://magnitcloud.by'
pathbot = 'c:\\inetpub\\wwwroot\\bot\\'
sleeptime = 6
global timestamps
timestamps = []
global sendernames
sendernames = []
      
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler('log.txt')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)     
def writelog(msg, type = ""):
    logger.info(type + "{0}".format(msg))
   
viber = Api(BotConfiguration(
  name='testbotnew',
  avatar='http://viber.com/avatar.jpg',
  auth_token=auth_token_viber
))

service_ ='https://smba.trafficmanager.net/apis/'

def getTime():
    strs = ""
    dt = datetime.now()
    strs = strs + "{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}{:03d}".format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, int(dt.microsecond/1000))
    #writelog(strs)
    return strs

 
def incomingViber(datadec):
    pathreceiveviber =  ftproot + "viber\\receive\\"   
    viber_request = viber.parse_request(datadec)
    #global mst
    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
        typer = message.to_dict().get("type")
        fullname = pathreceiveviber + getTime() + " " +str(viber_request.message_token) +".txt"
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
            namef = namef.replace('я',"%FF").replace('Я',"%FF")
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
    
def readTokens():
    try:
        bot = []
        f = open(pathbot+"tokens.cfg",'r')
        for line in f:            
            val = line.rstrip()
            boti = skypebot.SkypeBot("","",val)
            bot.append(boti)
            
        f.close()
        return bot
    except Exception as e:
        writelog("{0}".format(traceback.format_exc())) 
        pass 

def getTimeLoc(time_):
    rets = ""
    time_ = time_.split('+')[0]
    cnt = 0
    for s in time_ :
        if (s>='0' and s<='9') :
            rets = rets + s
            cnt = cnt + 1
    if len(rets)==15:
        rets = rets + '00'
    if len(rets)==16:
        rets = rets + '0'    
    return rets
    
def processMessSkype(data)
    sender = data.get('conversation').get('id')
    username = ''
    if 'from' in data and 'name' in data.get('from'):
        username = data.get('from').get('name')
    time_s =  getTimeLoc(data.get("localTimestamp")) +" "+ data.get('id')
    text = ''
    
    if 'text' in data:
        text = data.get('text')
        saveFileSkype(pathreceiveskype,sender,username, time_s, text,service)
    if 'attachments' in data:
        try:
            attachm = data.get('attachments')[0]
            curl = attachm.get('contentUrl')
            response = requests.get(curl, headers={"Authorization": "Bearer "+bot[indxbot].get_token(),"Content-Type":"application/json"},stream=True)
            filen =  getTimeLoc(data.get("localTimestamp")) +" "+ attachm.get('name').replace('я',"%FF").replace('Я',"%FF")
            filename = pathreceiveskype +'files\\' + filen 
            with open(filename, 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
            saveFileSkype(pathreceiveskype,sender,username, time_s, "<file> "+filen,service)
        except Exception as e:
            writelog("{0}".format(traceback.format_exc()),"skype")
            
def saveFileSkype(path, sender,name, time, text,service):
    try:
        fullname = path + time +".txt"
        f = open(fullname, 'w')
        f.write(name+'\n'+sender+'\n'+text+'\n') 
        f.close()
    except Exception as e:
        pass
        
def incomingSkype(data, indxbot):
    bot = readTokens()
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
            processMessSkype(data)    
        elif data['type'] == 'contactRelationUpdate':
            if data['action']=='add':
                sender = data['conversation']['id']
                bot[indxbot].send_message(service,sender,"Привет, я бот")
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
def retFile(type, file):
    try:
        file = file.replace("__"," ")
        if type == 'viber' or type.find('skype')>-1:
            files_pic = os.listdir(path=ftproot + type +"\\send\\files\\.")
            if (file in files_pic):
                return send_from_directory(ftproot + type +"\\send\\files\\", file )       
    except Exception as e:
        writelog("{0}".format(traceback.format_exc()),type)        
        
  
@app.route('/', methods=['POST','GET'])
def webhookOrigin():
    
    if request.method == 'GET':
        return "bot Запчасть Магнит ООО"
    if request.method == 'POST':
        try:
            reqde = request.data.decode('utf-8')
            if (len(reqde)>10):
                data = json.loads(reqde)
                if 'serviceUrl' in data:
                    writelog(reqde,"skype")
                    return incomingSkype(data,0)
                else:
                    writelog(reqde,"viber")
                    return incomingViber(reqde)    
        except Exception as e:
            writelog("{0}".format(traceback.format_exc()))  

    return 'Ok'
@app.route('/<type>', methods=['POST','GET'])
def webhook(type):
    if type.find("skype")>-1:
        if request.method == 'GET':
            return "bot "+type+ " Запчасть Магнит ООО"
        if request.method == 'POST':
            try:
                rdata = request.data.decode('utf-8')
                if (len(rdata)>10):
                    data = json.loads(rdata)
                    writelog(rdata,type)
                    return incomingSkype(data,int(type[-1]))
            except Exception as e:
                writelog("{0}".format(traceback.format_exc()))  
    return 'Ok'

if __name__ == '__main__': 
    app.run()