from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration

def writelog(msg):
    f = open("log_setup.txt", "a")
    f.write(msg+'\n')
    f.close()
website = ''
auth_token_viber = ''
f = open("config_bot.cfg",'r')
for line in f:
    var = line.split('=')[0]
    val = line.split('=')[1].rstrip()
    if var == 'website':
        website = val
    elif var == 'auth_token_viber':
        auth_token_viber = val

viber = Api(BotConfiguration(
  name='testbotnew',
  avatar='http://viber.com/avatar.jpg',
  auth_token=auth_token_viber
))

try:
    viber.set_webhook(website)
except Exception as e:
    writelog("{0}".format(e)) 
    pass 