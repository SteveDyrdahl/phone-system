import unittest
import phonesystem.twiliohelper


class TestTwilioHelper(unittest.TestCase):
    def test_getrejectresponse(self):
        xml = phonesystem.twiliohelper.getrejectresponse()
        expected = '<Response><Reject /></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test_gethangupresponse(self):
        xml = phonesystem.twiliohelper.gethangupresponse()
        expected = '<Response><Hangup /></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test_getvoicemailresponse(self):
        xml = phonesystem.twiliohelper.getvoicemailresponse('foo@bar.com')
        expected = '<Response><Redirect>https://twimlets.com/voicemail?Email=foo@bar.com&amp;' \
                   'Transcribe=false</Redirect></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test_getforwardresponse(self):
        xml = phonesystem.twiliohelper.getforwardresponse('111-111-1111')
        expected = '<Response><Redirect>https://twimlets.com/forward?PhoneNumber=111-111-1111' \
                   '</Redirect></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test_getsay(self):
        xml = phonesystem.twiliohelper.getsay('Hello World')
        expected = '<Say>Hello World</Say>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test_getsayandhangup(self):
        xml = phonesystem.twiliohelper.getsayandhangup('Hello World')
        expected = '<Response><Say>Hello World</Say><Hangup /></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)

    def test_getsayandgather(self):
        xml = phonesystem.twiliohelper.getsayandgather('Hello World', '/foo/bar')
        expected = '<Response><Gather numDigits="3" action="/foo/bar"><Pause />' \
                   '<Say>Hello World</Say></Gather><Hangup /></Response>'
        self.assertIsNot(xml.find(expected), -1, xml + ' does not contain ' + expected)


if __name__ == '__main__':
    unittest.main()
