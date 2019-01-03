# phone-system
## Overview
This phone system is for handling calls incoming to a Twilio phone number and routing the call to different end states depending on a number of factors.  This allows calls from known callers to be handled differently, to never accept calls from certain callers, and to have unknown callers verify they are an actual person by providing them with a challenge question.  An understanding of Twilio, AWS (S3, Lambda, API Gateway, CloudWatch, IAM), JSON, and Python3 will be needed to successfully setup your own instance.  Use at your own risk.  Missed phone calls, AWS charges, Twilio charges, etc. are solely your responsibility.

The table below summarizes the different possible end states for an incoming call and the the different ways that end state can be arrived at.  The table references the following: 
* __from__ The phone number of the caller. This value of course can be [spoofed](https://en.wikipedia.org/wiki/Caller_ID_spoofing).
* __challenge_question__ The caller is prompted to enter specific digits on their phone and their response is evaluated to determine whether or not they entered the correct digits or not.  Unanswered questions are tracked to handle [robocalls](https://en.wikipedia.org/wiki/Robocall).
* The following are provided as part of the configuration setup:
   * __addressbook__ A [vCard](https://en.wikipedia.org/wiki/VCard) formatted file.
   * __default_phone_number__ A valid phone number.
   * __voicemail_email_address__ A valid email address.
   * __failed_challenge_message__ A text string message that is used to inform callers that they have failed the __challenge_question__.  The implementation allows for two different messages.  One for the first and second time a caller has failed a __challenge_questions__ and a second one for when the caller has failed three or more __challenge_questions__.
   * __blacklist__ A list of phone numbers from which calls should never be accepted.
   * __forwardlist__ A list of phone numbers each one mapped to another phone number.
   * __graylist__ A list of phone numbers that map to two variables.  One variable that is a count of the number of times __from__ has been given a __challenge_question__ that has not been answered.  A second variable that is a count of the number of times __from__ has  incorrectly answered a __challenge_question__ consecutively.

End States | How to arrive at this end state?
----------------|----------------------------
Call is forwarded to __default_phone_number__|__from__ exists in __addressbook__
Call is forwarded to phone number mapped to by __from__ in __forwardlist__|__from__ exists in __forwardlist__
Call is [rejected](https://www.twilio.com/docs/voice/twiml/reject)<br>Caller hears a standard not-in-service message|__from__ exists in __blacklist__
Call is [rejected](https://www.twilio.com/docs/voice/twiml/reject)<br>Caller hears a standard not-in-service message|__from__ exists in __graylist__ and either the count of unanswered __challenge_questions__ or the count of consecutive incorrectly answered __challenge_questions__ is greater than or equal to 3
Call is sent to [Twilio voicemail](https://www.twilio.com/labs/twimlets/voicemail) and a link to the recording is emailed to __voicemail_email_address__|Caller successfully answered the challenge question
Caller hears __failed_challenge_message__ and then the call is [ended](https://www.twilio.com/docs/voice/twiml/hangup)|Caller provided a response to the __challenge_question__ that was incorrect


## Setup
These setup instructions will cover some/most of the specific information needed for setup.  They will not cover all the details needed to understand/setup your AWS environment (in particular all the permissions related settings).  The reference section provides links to additional information and "Build Your Own IVR..." in particular is useful as that was the starting point for this project.

### AWS S3
Create a S3 bucket that will store all of the configuration files necessary.  The Lamdba function (setup information below) will need read and write access to this bucket.
* A [vCard](https://en.wikipedia.org/wiki/VCard) formatted file which will be used as the addressbook.
   * The minimal implentation is an empty file.
   * If you are using iCloud, you can create an addressbook file by logging into iCloud, navigating to Contacts, click on the gear in the lower left, "Select All", click on the gear in the lower left, and "Export VCard...".
* A graylist json file.
   * The minimal implementation is a file containing:
       ```json
       {}
       ```
* A configuration file that will be referenced by the environment variable `PHONESYSTEM_CONFIG`.
   * A minimal implementation (that needs editing) is a file containing:
       ```json
       {
           "+10000000000": {
               "addressbook": "s3://bucketname/addressbook.vcf",
               "gatheraction": "/prod/phonesystem",
               "graylistlocation": "s3://bucketname/graylist.json",
               "updategraylist": "True",
               "phone": "555-555-5555",
               "voicemail": "simple@example.com"
           }
       }
       ```
   * The following edits are needed to the above example:
      * `+10000000000` will be replaced with your Twilio phone number.
      * `bucketname` will be replaced with the name of the S3 bucket where you setup to store the configuration files.
      * `addressbook.vcf` will be replaced with the key of the addressbook file you created and uploaded to the S3 bucket.
      * `graylist.json` will be replaced with the key of the graylist file you created and uploaded to the S3 bucket.
      * `/prod/phonesystem` will be replaced with the relative path to the API that will be setup using Amazon's API Gateway (more information below).
      * `555-555-5555` will be replaced with the phone number that you want calls forwarded to.
      * `simple@example.com` will be replaced with the email address you want voicemail notifications be sent to.
   * Other notes:
      * Technically `updategraylist` is not required.  However, it is required with a value of `True` if you want the count values to persist.
      * Other functionality (blacklist, forwardlist, multiple phone number support) are not included in this minimal example.  Example syntax can be found in the unit tests.

### AWS Lambda
You will need to create a Python 3 function to run this code.
* You will need to use the "Upload a file from Amazon S3" feature as the zip file will be too large to upload.  You can use the `dist-prepare.sh` and `dist-refresh.sh` scripts to create a zip file that is compatible with AWS Lambda.  Both scripts will need to be edited to set variables needed for execution.
* The Handler should be set to `phonesystem.callhandler.lambda_handler`.
* An environment variable `PHONESYSTEM_CONFIG` needs to exist with a value of `s3://bucketname/config_filename`
* The Timeout value might need bumped up.  (e.g. 15 seconds)

### AWS API Gateway
You will need to create an API that is the endpoint called by Twilio that will call the Lambda Function.  In this API, create a Resource and add a POST Method with an `Integration Type` of `Lambda Function`.  Twilio calls are all XML based which requires mapping in and out to be setup.  The "Build Your Own IVR..." reference below will provide details needed to understand what is going on and why.
* Integration Request
   * `Content Type` = `application/x-www-form-urlencoded`
   * Template
      ```
      {
         "body" : $input.json('$')
      }
      ```
* Integration Response
   * `Content Type` = `application/xml`
   * Template
      ```
      #set($inputRoot = $input.path('$')) 
      $inputRoot
      ```
* Method Response
   * `Content Type` = `application/xml`

The URL pattern for calling this API Gateway:<br)
`https://{restapi_id}.execute-api.{region}.amazonaws.com/{stage_name}/`

### AWS CloudWatch
Logging will show up in CloudWatch.

### Twilio
On the configuration page for your phone number in the "Voice & Fax" section you need to configure values for "A CALL COMES IN"
* Select `Webhook` in the first drop down.
* Enter the URL from the above API Gateway into the text box.
* Select 'HTTP POST' in the second drop down.
It is also suggested to configure values for the "PRIMARY HANDLER FAILS" section.  In the event that an unexpected error occurs, the call can still get routed to a valid end state.  Otherwise the caller will hear the default error message "an application error has occured".
* Select `Webhook` in the first drop down.
* Enter `http://twimlets.com/voicemail?Email=simple@example.com&Transcribe=false` into the text box. Make sure to substitute your email address into the example URL provided.
* Select 'HTTP POST' in the second drop down.

## Trouble Shooting
This section needs written.

## References
* [Build Your Own IVR with AWS Lambda, Amazon API Gateway and Twilio](https://www.twilio.com/blog/2015/09/build-your-own-ivr-with-aws-lambda-amazon-api-gateway-and-twilio.html)
* [Hassle-Free Python Lambda Deployment](https://joarleymoraes.com/hassle-free-python-lambda-deployment)
* [AWS Lambda Deployment Package in Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html)
