# -*- coding: utf-8 -*-

import threading

import sys
import requests
import time

from skypebot import skype_api

class SkypeBot:
    
    def __init__(self, client_id="",client_secret="",tok=""):             
        if tok != "":
            self.token = tok
        else:
            self.token = skype_api.generate_token(client_id, client_secret)
    def get_token(self):
        return self.token 
    
    def send_message(self,service,sender, text):
        return skype_api.send_message(self.token,service,sender, text)

    def create_card_image(self,url,alt=None):
        return skype_api.create_card_image(url,alt)
        
    def create_buttons(self,type,title,value):
        return skype_api.create_buttons(type,title,value)
        
    def create_card_attachment(self,type,title,subtitle=None,text=None,images=None,buttons=None):
        return skype_api.create_card_attachment(type,title,subtitle,text,images,buttons)

    def create_animation(self,type,url,images,title=None,subtitle=None,text=None,buttons=None):
        return skype_api.create_animation(type,url,images,title,subtitle,text,buttons)
    

    def send_media(self,service,sender,type,url):
        return skype_api.send_media(self.token,service,sender,type,url)
    def send_attachments(self,service,sender,data,thumbdata):
        return skype_api.send_attachments(self.token,service,sender,data,thumbdata)
        
    def send_card(self,service,sender,type,card_attachment,summary=None,text=None):
        return skype_api.send_card(self.token,service, sender,type,card_attachment,summary,text)
        
    #Not yet supported
    
    def send_action(self,service,sender):
        return skype_api.send_action(self.token,service,sender) 
