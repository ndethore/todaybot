import sys
import os
import time
import yaml
import traceback

from slackclient import SlackClient

outputs = []

class SlackBot(object):
    def __init__(self, token):
        self.last_ping = 0
        self.token = token
        self.bot_plugins = []
        self.slack_client = None

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
        user_id = data["user"]
        print "UserID:" + user_id
        if channel_id.startswith("D"):
            user_name = self.get_username(user_id)
            print "'{0}' just sent a message.".format(user_name)

    def get_username(self, user_id):
        # user = self.slack_client.api_call(["users.info", {"user":user_id}])
        if user:
            if user["first_name"]:
                return user["first_name"]
            else:
                return user["name"]


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
