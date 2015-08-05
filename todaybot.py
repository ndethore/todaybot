import sys
import os
import time
import yaml
import json
import traceback

from slackclient._user import User
from slackclient import SlackClient

outputs = []

class SlackBot(object):
    def __init__(self, token):
        self.last_ping = 0
        self.token = token
        self.bot_plugins = []
        self.slack_client = None
        self.users = None

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
        if "type" in data and data["type"] != "pong":
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
        # direct_channels = self.slack_client.api_call("im.list")
        # print "List of existing channels" + direct_channels

    def process_message(self, data):
        channel_id = data["channel"]
        user = None
        if channel_id.startswith("D"):
            user_id = data["user"]
            print "UserID:" + user_id

            # try: 
            #     user = self.users[user_id]
            # except KeyError:
            #     user = self.get_user(user_id)
            #     self.users.add(user)
            #     # print "'{0}' just sent a message.".format(user_name)
            #     print self.users

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
