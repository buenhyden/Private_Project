import sys  
from slacker import Slacker
import pickle
def slacktoken():
    #x = pickle.load(open('/Users/hyunyoun/Documents/slack_token','rb'))
    x = pickle.load(open('C:/Users/pc/Documents/GitHub/slack_token','rb'))
    return x['token']
def slack(token):
    return Slacker(token)

if __name__ == '__main__':
    slack = Slacker(slacktoken())
    slack.chat.post_message('#general','hello')