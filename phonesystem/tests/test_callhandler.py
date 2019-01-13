import os
import phonesystem.callhandler
import unittest


class TestCallHandler(unittest.TestCase):
    # TODO Do a proper setup and teardown.
    os.environ['PHONESYSTEM_CONFIG'] = 'phonesystem/tests/test_callhandler_config.json'

    def test1_addressbook(self):
        s1 = 'From=%2B11111111111&To=%2B10000000000'
        e = {'body': s1}
        xml = phonesystem.callhandler.lambda_handler(e, None)
        expected = '<Response><Redirect>https://twimlets.com/forward?PhoneNumber=123-123-0000' \
                   '</Redirect></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test1_blacklist1(self):
        s1 = 'From=%2B16666666666&To=%2B10000000000'
        e = {'body': s1}
        xml = phonesystem.callhandler.lambda_handler(e, None)
        expected = '<Response><Reject /></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test1_blacklist2(self):
        s1 = 'From=%2B16666666663&To=%2B10000000000'
        e = {'body': s1}
        xml = phonesystem.callhandler.lambda_handler(e, None)
        expected = '<Response><Reject /></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test1_forwardlist(self):
        s1 = 'From=%2B18888888888&To=%2B10000000000'
        e = {'body': s1}
        xml = phonesystem.callhandler.lambda_handler(e, e)
        expected = '<Response><Redirect>https://twimlets.com/forward?PhoneNumber=111-222-3333' \
                   '</Redirect></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test1_graylist1(self):
        s1 = 'From=%2B17777777777&To=%2B10000000000'
        e = {'body': s1}
        xml = phonesystem.callhandler.lambda_handler(e, e)
        expected = '<Response><Gather numDigits="3" action="/dev/phonesystem"><Pause />' \
                   '<Say>enter 7 7 7 followed by pound</Say></Gather><Hangup /></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test1_graylist2(self):
        s1 = 'From=%2B17777777777&To=%2B10000000000&Digits=777'
        e = {'body': s1}
        xml = phonesystem.callhandler.lambda_handler(e, e)
        expected = '<Response><Redirect>https://twimlets.com/voicemail?Email=foo@bar.com' \
                   '&amp;Transcribe=false</Redirect></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test1_graylist3(self):
        s1 = 'From=%2B17777777777&To=%2B10000000000&Digits=770'
        e = {'body': s1}
        xml = phonesystem.callhandler.lambda_handler(e, e)
        expected = '<Response><Say>Unfortunately you have failed the challenge test. Good bye.' \
                   '</Say><Hangup /></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)
        xml = phonesystem.callhandler.lambda_handler(e, e)
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)
        xml = phonesystem.callhandler.lambda_handler(e, e)
        expected = '<Response><Say>Unfortunately you have failed the challenge test three consecutive times ' \
                   'and have been added to the do not accept list. Good bye.</Say><Hangup /></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test1_unanswered(self):
        s1 = 'From=%2B17777777779&To=%2B10000000000'
        e = {'body': s1}
        xml = phonesystem.callhandler.lambda_handler(e, e)
        expected = '<Response><Gather numDigits="3" action="/dev/phonesystem"><Pause />' \
                   '<Say>enter 7 7 9 followed by pound</Say></Gather><Hangup /></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)
        xml = phonesystem.callhandler.lambda_handler(e, e)
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)
        xml = phonesystem.callhandler.lambda_handler(e, e)
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)
        xml = phonesystem.callhandler.lambda_handler(e, e)
        expected = '<Response><Reject /></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test2_addressbook(self):
        s1 = 'From=%2B11111111111&To=%2B10000000001'
        e = {'body': s1}
        xml = phonesystem.callhandler.lambda_handler(e, None)
        expected = '<Response><Redirect>https://twimlets.com/forward?PhoneNumber=123-123-0002' \
                   '</Redirect></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test2_blacklist(self):
        s1 = 'From=%2B16666666662&To=%2B10000000001'
        e = {'body': s1}
        xml = phonesystem.callhandler.lambda_handler(e, None)
        expected = '<Response><Reject /></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test2_forwardlist(self):
        s1 = 'From=%2B18888888888&To=%2B10000000001'
        e = {'body': s1}
        xml = phonesystem.callhandler.lambda_handler(e, e)
        expected = '<Response><Redirect>https://twimlets.com/forward?PhoneNumber=111-222-3332' \
                   '</Redirect></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test2_graylist1(self):
        s1 = 'From=%2B17777777772&To=%2B10000000001'
        e = {'body': s1}
        xml = phonesystem.callhandler.lambda_handler(e, e)
        expected = '<Response><Gather numDigits="3" action="/dev/phonesystem2"><Pause />' \
                   '<Say>to be connected with bob, enter the digits 7 7 2 followed by #</Say></Gather>' \
                   '<Hangup /></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test2_graylist2(self):
        s1 = 'From=%2B17777777772&To=%2B10000000001&Digits=772'
        e = {'body': s1}
        xml = phonesystem.callhandler.lambda_handler(e, e)
        expected = '<Response><Redirect>https://twimlets.com/voicemail?Email=foo2@bar.com' \
                   '&amp;Transcribe=false</Redirect></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test2_graylist3(self):
        s1 = 'From=%2B17777777772&To=%2B10000000001&Digits=770'
        e = {'body': s1}
        xml = phonesystem.callhandler.lambda_handler(e, e)
        expected = '<Response><Say>Unfortunately you have failed the challenge test. Good bye.' \
                   '</Say><Hangup /></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)
        xml = phonesystem.callhandler.lambda_handler(e, e)
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)
        xml = phonesystem.callhandler.lambda_handler(e, e)
        expected = '<Response><Say>Unfortunately you have failed the challenge test three consecutive times ' \
                   'and have been added to the do not accept list. Good bye.</Say><Hangup /></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)


if __name__ == '__main__':
    unittest.main()
