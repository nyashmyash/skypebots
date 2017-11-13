# -*- coding: utf-8 -*-

import sys
import os
import requests
import string
import threading
import time
from datetime import datetime
import skypebot
import urllib
import traceback
import logging
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.file_message import FileMessage

auth_token_viber='--'
ftproot = "C:\\Inetpub\\ftproot\\"
website = 'https://magnitcloud.by'
pathbot = 'c:\\inetpub\\wwwroot\\bot\\'
sleeptime = 6
     
logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler('log_new.txt')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)  

skypedata =[["--"],
    ["--"]]
    

def readvars():
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
        
def writelog(msg, type = ""):
    logger.info(type + "{0}".format(msg))
   
viber = Api(BotConfiguration(
  name='testbotnew',
  avatar='http://viber.com/avatar.jpg',
  #auth_token='46d4d869e6e7d0bf-427b852bca964b59-6df0847c332b71c7'
  auth_token=auth_token_viber
))

service_ ='https://smba.trafficmanager.net/apis/'

def getTime():
    strs = ""
    dt = datetime.now()
    strs = strs + "{:04d}{:02d}{:02d}{:02d}{:02d}{:02d}{:03d}".format(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, int(dt.microsecond/1000))
    #writelog(strs)
    return strs
def getfiles(bot,type_bot, indxbot = -1):
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
                    linef = lines[2].replace("<file>","").strip()                   
                    if fnp == linef:
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
                    #writelog(messeges, type_bot)
                    if type_bot == 'viber':
                        try:
                            viber.send_messages(lines[1], [
                                TextMessage(None, None, messeges)
                            ])
                            #if(os.path.isfile(pathsend+fn)):
                            #    os.replace(pathsend+fn, pathsend+"sended\\"+fn)
                        except Exception as e:
                            writelog("{0}".format(traceback.format_exc()),type_bot) 
                            pass
                    elif indxbot != -1:
                        bot[indxbot].send_message(service_,lines[1],messeges) 
                        #if(os.path.isfile(pathsend+fn)):
                        #    os.replace(pathsend+fn, pathsend+"sended\\"+fn)
               
            
    except Exception as e:
        writelog("{0}".format(traceback.format_exc()),type_bot) 
        
        pass

def functhr(bot):
    getfiles(bot,'skype', 0)
    k = 1
    while k < 10:
        getfiles(bot,'skype' + str(k), k)
        k = k + 1
    getfiles(bot,'viber')

class ClockThread(threading.Thread):
    def __init__(self,interval):
        threading.Thread.__init__(self)
        #self.daemon = True
        self.interval = interval
    def run(self):
        while True:
            time.sleep(self.interval)
            #if len(bot) != 0:
                #writelog(str(len(bot)))
            functhr(readvars())
 

def restartbot():
    f = open("tokens.cfg", mode="w")
    for dat in skypedata:
        boti = skypebot.SkypeBot(dat[0],dat[1])
        f.write("{0}\n".format(boti.token))
    f.close()
    
def skype_restart(interval):
    while True:
        restartbot()
        print("restart")
        time.sleep(interval)
        
t1 = threading.Thread(target=skype_restart, args=(2000,))
t1.daemon = True
t1.start()


t = ClockThread(sleeptime)
t.start() 
