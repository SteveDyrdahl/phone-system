# phone-system
## Overview
This phone system is for handling calls incoming to a Twilio phone number and routing the call to different end states depending on a number of factors.  An understanding of Twilio, AWS, JSON, and Python will be needed to successfully setup your own instance.  Use at your own risk.  Missed phone calls, AWS charges, Twilio charges, etc. are solely your responsibility.

The table below summarizes the different possible end states for an incoming call and the the different ways that end state can be arrived at.  The table references the following: 
* __from__ The phone number of the caller which of course can be [spoofed](https://en.wikipedia.org/wiki/Caller_ID_spoofing).
* The following are provided as part of the configuration setup:
** __addressbook__ A [vCard](https://en.wikipedia.org/wiki/VCard) formatted file.
** __default_phone_number__ A valid phone number.
** __blacklist__ A list of phone numbers.
** __forwardlist__ A list of phone numbers each one mapped to another phone number.
** __graylist__ A list of phone numbers that map to two variables.  One variable that is a count of the number of times __from__ has been given a challenge question that has not been answered.  A second variable that is a count of the number of times __from__ has incorrectly answered a challenge question.

End States | How to arrive at this end state?
----------------|----------------------------
Call is forwarded to __default_phone_number__.|__from__ exists in __addressbook__.
Call is forwarded to phone number mapped to in __forwardlist__.|__from__ exists in __forwardlist__.
Call is [rejected](https://www.twilio.com/docs/voice/twiml/reject).  Caller hears a standard not-in-service message.|__from__ exists in __blacklist__. 

## References
* [Build Your Own IVR with AWS Lambda, Amazon API Gateway and Twilio](https://www.twilio.com/blog/2015/09/build-your-own-ivr-with-aws-lambda-amazon-api-gateway-and-twilio.html)
* [Hassle-Free Python Lambda Deployment](https://joarleymoraes.com/hassle-free-python-lambda-deployment)
* [AWS Lambda Deployment Package in Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html)
