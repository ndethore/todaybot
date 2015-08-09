import sys
import os
import time
import yaml
import json
import traceback
import random
from datetime import datetime
from pytz import timezone

from slackclient._user import User
from slackclient import SlackClient

class Survey(object):
    def __init__(self, user):
        self.user = user
        self.answers = {}
        self.currentStep = 0
        self.stepMessageMap = { 0:self.done_message,\
                                1:self.unfinished_message,\
                                2:self.todo_message,\
                                3:self.issue_message }

        self.cheerings = ["Great", "Good", "Awesome"]
        print "Survey created for {}.".format(user.real_name)


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
        print self.user
        if self.user.real_name:
            name = self.user.real_name
        else:
            name = self.user.name

        return "Hi {} !\nWhat did you do yesterday ?".format(name)

    def unfinished_message(self):
        return "Anything that you couldn't finish ?"

    def todo_message(self):
        return "What's your plan for today ?"

    def issue_message(self):
        return "Any issues ?"

    def more_message(self):
        index = random.randint(0, 2)
        return self.cheerings[index] + " ! Anything else ?"

    def toString(self):
        string = "[Done]\n"
        for answer in self.answers[0]:
            string += "- {}\n".format(answer)

        string += "\n[Unfinished]\n"
        for answer in self.answers[1]:
            string += "- {}\n".format(answer)

        string += "\n[Todo]\n"
        for answer in self.answers[2]:
            string += "- {}\n".format(answer)

        string += "\n[Issue]\n"
        for answer in self.answers[3]:
            string += "- {}\n".format(answer)

        return string





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
        if channel_id.startswith("D"):
            user_id = data["user"]
            print "UserID:" + user_id

            if user_id not in self.surveys:
                user = self.get_user(user_id)
                self.surveys.update({user_id:Survey(user)})
            survey = self.surveys[user_id]

            output = survey.process_input(data["text"])
            if output:
                self.send_message(output, channel_id)
            else:
                todo_channel = self.slack_client.server.channels.find(todo_channel_id)
                if todo_channel == None:
                    todo_channel = self.slack_client.server.channels.find(channel_id)
                if self.create_post(survey.user, survey.toString(), todo_channel.id) == False:
                    self.send_message(survey.toString(), todo_channel.id)
                self.send_message("Todo list sucessfully shared.\nHave a nice day !", channel_id)


    def send_message(self, message, channel_id):
        channel = self.slack_client.server.channels.find(channel_id)
        encoded_message = message.encode('ascii','ignore')

        channel.send_message("{}".format(encoded_message))


    def create_post(self, user, content, channel_id):
        now = datetime.now(timezone(user.tz))
        title = "[{}] ".format(user.real_name)
        title += "{0} {1} {2}".format(now.year, now.month, now.day)

        server_response = self.slack_client.api_call("files.upload",
                                                    content=content,
                                                        title=title,
                                                        channels=channel_id).decode('utf-8')
        print server_response
        data = json.loads(server_response)
        print data
        success = False
        if "ok" in data:
            success = data["ok"]
        return success


    def get_user(self, user_id):
        response = self.slack_client.api_call("users.info", user=user_id).decode('utf-8')
        data = json.loads(response)
        if data["ok"]:
            user = data["user"]
            profile = user["profile"]
            first_name = None
            if "first_name" in profile:
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
    todo_channel_id = config["TODO_CHANNEL"]
    main_loop()
