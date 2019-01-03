# TODO URL parameters are not encoded and therefore invalid URLs could be created from configurable inputs.
_OPEN_RESPONSE = '<?xml version="1.0" encoding="UTF-8"?><Response>'
_CLOSE_RESPONSE = '</Response>'
_REJECT_RESPONSE = _OPEN_RESPONSE + '<Reject />' + _CLOSE_RESPONSE
_HANGUP = '<Hangup />'
_HANGUP_RESPONSE = _OPEN_RESPONSE + _HANGUP + _CLOSE_RESPONSE
_OPEN_GATHER = '<Gather numDigits="3" action="X">'
_CLOSE_GATHER = '</Gather>'
_OPEN_REDIRECT = '<Redirect>'
_CLOSE_REDIRECT = '</Redirect>'
_OPEN_SAY = '<Say>'
_CLOSE_SAY = '</Say>'
_PAUSE = '<Pause />'
_TWIMLETS_URL = 'https://twimlets.com/'

def getrejectresponse():
    return _REJECT_RESPONSE


def gethangupresponse():
    return _HANGUP_RESPONSE


def getsay(message: str):
    return _OPEN_SAY + message + _CLOSE_SAY


def getsayandhangup(message: str):
    return _OPEN_RESPONSE + getsay(message) + _HANGUP + _CLOSE_RESPONSE


def getsayandgather(message: str, action: str):
    return _OPEN_RESPONSE + _OPEN_GATHER.replace('X', action) + _PAUSE + getsay(message) + \
           _CLOSE_GATHER + _HANGUP + _CLOSE_RESPONSE


def getvoicemailresponse(email: str):
    return _OPEN_RESPONSE + _OPEN_REDIRECT + _TWIMLETS_URL + 'voicemail?Email=' + email + '&amp;Transcribe=false' +\
           _CLOSE_REDIRECT + _CLOSE_RESPONSE


def getforwardresponse(phone: str):
    return _OPEN_RESPONSE + _OPEN_REDIRECT + _TWIMLETS_URL + 'forward?PhoneNumber=' + phone + _CLOSE_REDIRECT +\
           _CLOSE_RESPONSE
