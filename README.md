# phone-system
## Overview
This phone system is for handling calls incoming to a Twilio phone number and routing the call to different end states depending on a number of factors.  An understanding of Twilio, AWS, JSON, and Python 3 will be needed to successfully setup your own instance.  Use at your own risk.  Missed phone calls, AWS charges, Twilio charges, etc. are solely your responsibility.

The table below summarizes the different possible end states for an incoming call and the the different ways that end state can be arrived at.  The table references the following: 
* __from__ The phone number of the caller which of course can be [spoofed](https://en.wikipedia.org/wiki/Caller_ID_spoofing).
* __challenge_question__ The caller is prompted to enter specific digits on their phone and their response is evaluated to determine whether or not they entered the correct digits or not.  Unanswered questions are tracked to handle [robocalls](https://en.wikipedia.org/wiki/Robocall).
* The following are provided as part of the configuration setup:
   * __addressbook__ A [vCard](https://en.wikipedia.org/wiki/VCard) formatted file.
   * __default_phone_number__ A valid phone number.
   * __voicemail_email_address__ A valid email address.
   * __failed_challenge_message__ A text string message that is used to inform callers that they have failed the __challenge_question__.  The implementation allows for two different messages.  One for the first and second time a caller has failed a __challenge_questions__ and a second one for when the caller has failed three or more __challenge_questions__.
   * __blacklist__ A list of phone numbers.
   * __forwardlist__ A list of phone numbers each one mapped to another phone number.
   * __graylist__ A list of phone numbers that map to two variables.  One variable that is a count of the number of times __from__ has been given a __challenge_question__ that has not been answered.  A second variable that is a count of the number of times __from__ has  incorrectly answered a __challenge_question__ consecutively.

End States | How to arrive at this end state?
----------------|----------------------------
Call is forwarded to __default_phone_number__|__from__ exists in __addressbook__.
Call is forwarded to phone number mapped to by __from__ in __forwardlist__|__from__ exists in __forwardlist__.
Call is [rejected](https://www.twilio.com/docs/voice/twiml/reject)<br>Caller hears a standard not-in-service message|__from__ exists in __blacklist__
Call is [rejected](https://www.twilio.com/docs/voice/twiml/reject)<br>Caller hears a standard not-in-service message|__from__ exists in __graylist__ and either the count of unanswered __challenge_questions__ or the count of consecutive incorrectly answered __challenge_questions__ is greater than or equal to 3
Call is sent to [Twilio voicemail](https://www.twilio.com/labs/twimlets/voicemail) and a link to the recording is emailed to __voicemail_email_address__.|Caller successfully answered the challenge question.
Caller hears __failed_challenge_message__ and then the call is [ended](https://www.twilio.com/docs/voice/twiml/hangup).|Caller provided a response to the __challenge_question__ that was incorrect.


## Setup
### AWS S3
Create a S3 bucket that will store all of the configuration files necessary.
* A vCard](https://en.wikipedia.org/wiki/VCard) formatted file which will be used as the addressbook.
   * The minimal implentation is an empty file.
   * If you are using iCloud, you can create an addressbook file by logging into iCloud, navigating to Contacts, click on the gear in the lower left, "Select All", click on the gear in the lower left, and "Export VCard...".
* A graylist json file.
   * The minimal implementation is a file containing:
       ```json
       {}
       ```
* A configuration file that will be referenced by the environment variable `PHONESYSTEM_CONFIG`.  A minimal implementation (that needs editing) is a file containing:
       ```json
       {
           "+10000000000": {
               "addressbook": "s3://bucketname/addressbook.vcf",
               "gatheraction": "/prod/phonesystem",
               "graylistlocation": "s3://bucketname/graylist.json",
               "phone": "555-555-5555",
               "voicemail": "simple@example.com"
           }
       }
       ```


## References
* [Build Your Own IVR with AWS Lambda, Amazon API Gateway and Twilio](https://www.twilio.com/blog/2015/09/build-your-own-ivr-with-aws-lambda-amazon-api-gateway-and-twilio.html)
* [Hassle-Free Python Lambda Deployment](https://joarleymoraes.com/hassle-free-python-lambda-deployment)
* [AWS Lambda Deployment Package in Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html)
