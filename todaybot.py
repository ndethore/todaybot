import sys
import os
import time
import yaml

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
        self.slack_client.rtm_connect()

    def process_hello(data):
        print "Connection established with server..."

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
        print data


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
