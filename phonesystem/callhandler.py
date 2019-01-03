from datetime import datetime
import json
import logging
import os
from phonesystem import addressbook
from phonesystem import twiliohelper
from phonesystem import util
import urllib.parse
import urllib.request


# Entry point for AWS Lambda
def lambda_handler(event, context):
    t1 = datetime.today()
    # Use a shared instance to avoid multiple initializations when the same Lambda instance is reused.
    callhandler = CallHandler.get_shared_instance(os.environ['PHONESYSTEM_CONFIG'])
    result = callhandler.handle_call(event['body'])
    t2 = datetime.today()
    logging.info(t2 - t1)
    return result


class HandlerConfig:
    _addressbook = None
    _phone = ''
    _voicemail = ''
    _gatheraction = ''
    _forwardlist = {}
    _blacklist = {}
    _updategraylist = False
    _graylistlocation = ''
    _graylist = {}
    _failedchallengemsg = 'Unfortunately you have failed the challenge test. Good bye.'
    _failedchallenge3plusmsg = 'Unfortunately you have failed the challenge test three consecutive times ' \
                               'and have been added to the do not accept list. Good bye.'

    def __init__(self, config: dict):
        # TODO Currently hard-coded to US phone numbers.
        self._addressbook = addressbook.AddressBook.get_shared_instance('1', 10, config['addressbook'])
        self._phone = config['phone']
        self._voicemail = config['voicemail']
        self._gatheraction = config['gatheraction']
        if 'forwardlist' in config:
            self._forwardlist = config['forwardlist']
        else:
            self._forwardlist = {}
        if 'blacklist' in config:
            self._blacklist = config['blacklist']
        else:
            self._blacklist = {}
        if 'updategraylist' in config:
            self._updategraylist = bool(config['updategraylist'] == 'True')
        # TODO Currently if two different configurations use the same graylist, they will over-ride each other.
        self._graylistlocation = config['graylistlocation']
        self._graylist = json.loads(util.get_file(self._graylistlocation))
        if 'failedchallengemsg' in config:
            self._failedchallengemsg = config['failedchallengemsg']
        if 'failedchallenge3plusmsg' in config:
            self._failedchallenge3plusmsg = config['failedchallenge3plusmsg']

    def get_addressbook(self):
        return self._addressbook

    def get_phone(self):
        return self._phone

    def get_voicemail(self):
        return self._voicemail

    def get_gatheraction(self):
        return self._gatheraction

    def in_forward_list(self, from_: str):
        return from_ in self._forwardlist

    def get_forward_value(self, from_: str):
        if self.in_forward_list(from_):
            return self._forwardlist[from_]
        else:
            return None

    def in_black_list(self, from_: str):
        return from_ in self._blacklist

    def exceeded_challenges(self, from_: str):
        unanswered_challenge = 0
        failed_challenge = 0
        if from_ in self._graylist:
            values = self._graylist[from_]
            if 'unanswered_challenge' in values:
                unanswered_challenge = max(values['unanswered_challenge'], 0)
            if 'failed_challenge' in values:
                failed_challenge = max(values['failed_challenge'], 0)
        return unanswered_challenge >= 3 or failed_challenge >= 3

    def increment_unanswered_challenge(self, from_: str):
        unanswered_challenge = 0
        failed_challenge = 0
        if from_ in self._graylist:
            values = self._graylist[from_]
            if 'unanswered_challenge' in values:
                unanswered_challenge = max(values['unanswered_challenge'], 0)
            if 'failed_challenge' in values:
                failed_challenge = max(values['failed_challenge'], 0)
        unanswered_challenge += 1
        self._update_graylist(from_, unanswered_challenge, failed_challenge)

    def decrement_unanswered_challenge(self, from_: str):
        unanswered_challenge = 1
        failed_challenge = 0
        if from_ in self._graylist:
            values = self._graylist[from_]
            if 'unanswered_challenge' in values:
                unanswered_challenge = max(values['unanswered_challenge'], 1)
            if 'failed_challenge' in values:
                failed_challenge = max(values['failed_challenge'], 0)
        unanswered_challenge -= 1
        self._update_graylist(from_, unanswered_challenge, failed_challenge)

    def passed_challenge(self, from_: str):
        self._update_graylist(from_, 0, 0)

    def failed_challenge(self, from_: str):
        unanswered_challenge = 0
        failed_challenge = 0
        if from_ in self._graylist:
            values = self._graylist[from_]
            if 'unanswered_challenge' in values:
                unanswered_challenge = max(values['unanswered_challenge'], 0)
            if 'failed_challenge' in values:
                failed_challenge = max(values['failed_challenge'], 0)
        failed_challenge += 1
        self._update_graylist(from_, unanswered_challenge, failed_challenge)

    def get_failed_challenge_msg(self, from_: str):
        if self.exceeded_challenges(from_):
            return self._failedchallenge3plusmsg
        else:
            return self._failedchallengemsg

    def _update_graylist(self, from_: str, unanswered_challenge: int, failed_challenge: int):
        self._graylist[from_] = {'unanswered_challenge': unanswered_challenge, 'failed_challenge': failed_challenge}
        if self._updategraylist:
            util.put_file(self._graylistlocation, json.dumps(self._graylist, sort_keys=True, indent=4))


class CallHandler:
    __shared_instances = {}
    _configurations = None
    _blacklist = {}

    def __init__(self, config_file: str):
        CallHandler._logging_setup()
        cfg = json.loads(util.get_file(config_file))
        self._configurations = {}
        for to in cfg:
            if to == 'blacklist':
                self._blacklist = cfg[to]
            else:
                self._configurations[to] = HandlerConfig(cfg[to])

    def handle_call(self, body: str):
        logging.info(body)
        keyvaluepairs = CallHandler._extractkeyvaluepairs(body)
        from_ = keyvaluepairs['From']
        to = keyvaluepairs['To']
        digits = None
        if 'Digits' in keyvaluepairs:
            digits = keyvaluepairs['Digits']
        xml = self._call_logic(from_, to, digits)
        logging.info(from_ + ':' + to + ':' + xml)
        return xml

    def _call_logic(self, from_: str, to: str, digits: str):
        config = self._configurations[to]
        # If digits is provided, then a challenge has been answered.
        if digits is not None:
            config.decrement_unanswered_challenge(from_)
        # Forward to phone if caller in address book.
        if config.get_addressbook().containsphonenumber(from_):
            return twiliohelper.getforwardresponse(config.get_phone())
        # Forward to configured number if caller in forward list.
        elif config.in_forward_list(from_):
            return twiliohelper.getforwardresponse(config.get_forward_value(from_))
        # Reject if caller in black list.
        elif config.in_black_list(from_) or from_ in self._blacklist:
            return twiliohelper.getrejectresponse()
        # Reject if caller has exceeded the number of failed challenges.
        elif config.exceeded_challenges(from_):
            return twiliohelper.getrejectresponse()
        # Challenge the caller to enter a numerical value on their phone.
        else:
            value = CallHandler._getchallengevalue(from_)
            # No digits provided indicates initial request, prompt the user for challenge input.
            if digits is None:
                config.increment_unanswered_challenge(from_)
                return twiliohelper.getsayandgather(CallHandler._getchallengemsg(value), config.get_gatheraction())
            # Caller correctly entered the challenge value.
            elif digits == value:
                config.passed_challenge(from_)
                return twiliohelper.getvoicemailresponse(config.get_voicemail())
            # Caller failed to correctly enter the challenge value. Let the caller know they failed and hangup.
            else:
                config.failed_challenge(from_)
                return twiliohelper.getsayandhangup(config.get_failed_challenge_msg(from_))

    @staticmethod
    def _extractkeyvaluepairs(body: str):
        key_value_pairs = {}
        key_values = body.split("&")
        for x in key_values:
            y = x.split("=")
            key_value_pairs[y[0]] = urllib.parse.unquote(y[1])
        return key_value_pairs

    # TODO: Make this message configurable.
    @staticmethod
    def _getchallengemsg(value: str):
        return 'enter ' + value[0] + ' ' + value[1] + ' ' + value[2] + ' followed by pound'

    @staticmethod
    def _getchallengevalue(caller: str):
        value = '360'
        if (len(caller) >= 3) and caller[-3:].isdigit():
            i = caller[-3:]
            if int(i) > 99:
                value = i
        return value

    @staticmethod
    def _logging_setup():
        # TODO Implement a solution that is more configurable (and elegant).
        root = logging.getLogger()
        if root.handlers:
            for handler in root.handlers:
                root.removeHandler(handler)
        logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

    @staticmethod
    def get_shared_instance(config_file: str):
        if config_file not in CallHandler.__shared_instances:
            CallHandler.__shared_instances[config_file] = CallHandler(config_file)
        return CallHandler.__shared_instances[config_file]
