todaybot
================
A simple conversational slackbot to generate daily pre-SCRUM todo lists.


Installation
----------

1. Download the todaybot code

    	$ git clone https://github.com/ndethore/todaybot.git
    
2. Install dependencies (virtualenv is recommended.)

    	$ pip install -r requirements.txt

3. Configure todaybot with a [user token](https://api.slack.com/web) or a [bot token](https://api.slack.com/bot-users)
    
		$ vi bot.conf
		
    	SLACK_TOKEN: "xoxb-11111111111-222222222222222"
    	TODO_CHANNEL: "#somechannel"

Usage
-----

	python todaybot.py

_Note:_ You must obtain a token for the user/bot. You can find or generate these at the [Slack API](https://api.slack.com/web) page.


TODO
----
* Add a timer to let the user input multiple items without interuptions.
* Export the questions / answers to an external files for internationalization/customization.
* Export the list title and content format for more flexibilty.
