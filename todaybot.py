import sys
import os
import time
import yaml
import json
import traceback
import random
import time

from slackclient._user import User
from slackclient import SlackClient

outputs = []

class Survey(object):
    def __init__(self, name):
        self.username = name
        self.answers = {}
        self.currentStep = 0
        self.stepMessageMap = { 0:self.done_message,\
                                1:self.unfinished_message,\
                                2:self.todo_message,\
                                3:self.issue_message }

        self.cheerings = ["Great", "Good", "Awesome"]

        print "Survey created for {}.".format(name)

    def process_input(self, user_input):
            
        if self.currentStep in self.answers:
            if "no" in user_input.lower():

                self.currentStep += 1
            else:
                self.answers[self.currentStep].append(user_input)
                return self.more_message()
        
        if self.currentStep < len(self.stepMessageMap):
            self.answers[self.currentStep] = []
            return self.stepMessageMap[self.currentStep]()
        else:
            return None


    def done_message(self):
        return "Hi {} !\nWhat did you do yesterday ?".format(self.username)

    def unfinished_message(self):
        return "Anything that you couldn't finish ?"

    def todo_message(self):
        return "What's your plan for today ?"

    def issue_message(self):
        return "Any issues ?"

    def more_message(self):
        index = random.randint(0, 2)
        return self.cheerings[index] + " ! Anything else ?"



class SlackBot(object):
    def __init__(self, token):
        self.last_ping = 0
        self.token = token
        self.bot_plugins = []
        self.slack_client = None
        self.surveys = {}

    def connect(self):
        """Convenience method that creates Server instance"""
        self.slack_client = SlackClient(self.token)
        try:
            self.slack_client.rtm_connect()
        except:
            print "Connection Failed, invalid token?"

    def start(self):
        self.connect()
        while True:
            for reply in self.slack_client.rtm_read():
                self.input(reply)
            self.autoping()
            time.sleep(.1)

    def autoping(self):
        #hardcode the interval to 3 seconds
        now = int(time.time())
        if now > self.last_ping + 3:
            self.slack_client.server.ping()
            self.last_ping = now

    def input(self, data):
        if "type" in data and data["type"]  != "pong":
            print data
            type = data["type"]
            function_name = "process_" + type
            try:
                getattr(self, function_name)(data)
            except AttributeError:
                print "Error: No '" + type + "' event handling."
            except:
                print traceback.print_exc()

    def process_hello(self, data):
        print "Connection established with server..."

    def process_message(self, data):
        channel_id = data["channel"]
        user = None
        if channel_id.startswith("D"):
            user_id = data["user"]
            print "UserID:" + user_id

            if user_id not in self.surveys:
                user = self.get_user(user_id)
                self.surveys.update({user_id:Survey(user.real_name)})

            survey = self.surveys[user_id]
            output = survey.process_input(data["text"])
            print output
            if output:
                self.send_message(output, channel_id)
                
    def send_message(self, message, channel_id):

        channel = self.slack_client.server.channels.find(channel_id)
        encoded_message = message.encode('ascii','ignore')
        channel.send_message("{}".format(encoded_message))
        

    def get_user(self, user_id):
        response = self.slack_client.api_call("users.info", user=user_id).decode('utf-8')
        data = json.loads(response)
        if data["ok"]:
            user = data["user"]
            profile = user["profile"]
            first_name = None
            if profile["first_name"]:
                first_name = profile["first_name"]

        return User(self, user["name"], user_id, first_name, user["tz"])


def main_loop():
    try:
        bot.start()
    except KeyboardInterrupt:
        sys.exit(0)
    except:
        print("Something went wrong :(")


if __name__ == "__main__":
    config = yaml.load(file('bot.conf', 'r'))
    bot = SlackBot(config["SLACK_TOKEN"])
    main_loop()
