import unittest
from phonesystem.addressbook import AddressBook


class TestAddressBook(unittest.TestCase):
    def test_containsphonenumber(self):
        addressbook = AddressBook('1', 10, 'phonesystem/tests/test_addressbook.vcf')
        self.assertTrue(addressbook.containsphonenumber('1111111111'))
        self.assertTrue(addressbook.containsphonenumber('+11111111111'))
        self.assertTrue(addressbook.containsphonenumber('+1 (111) 111-1111'))
        self.assertTrue(addressbook.containsphonenumber('111.111.1111'))
        self.assertTrue(addressbook.containsphonenumber(' (111)  111-1111'))
        self.assertTrue(addressbook.containsphonenumber('2222222222'))
        self.assertTrue(addressbook.containsphonenumber('3333333333'))
        self.assertTrue(addressbook.containsphonenumber('8004444444'))
        self.assertTrue(addressbook.containsphonenumber('4444444444'))
        self.assertTrue(addressbook.containsphonenumber('+91 (55) 55555555'))
        self.assertFalse(addressbook.containsphonenumber('9999999999'))

    def test_sharedinstance(self):
        addressbook1 = AddressBook('1', 10, 'phonesystem/tests/test_addressbook.vcf')
        addressbook2 = AddressBook('1', 10, 'phonesystem/tests/test_addressbook.vcf')
        addressbook3 = AddressBook.get_shared_instance('1', 10, 'phonesystem/tests/test_addressbook.vcf')
        addressbook4 = AddressBook.get_shared_instance('1', 10, 'phonesystem/tests/test_addressbook.vcf')
        self.assertTrue(addressbook1 != addressbook2)
        self.assertTrue(addressbook3 == addressbook4)


if __name__ == '__main__':
    unittest.main()
