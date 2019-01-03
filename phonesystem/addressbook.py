import vobject
import phonesystem.util


class AddressBook:
    __shared_instances = {}
    _countrycode = ''
    _phonenumberlength = 0
    _phonenumbers = {}

    def __init__(self, countrycode: str, phonenumberlength: int, addressbookfile: str):
        self._countrycode = countrycode
        self._phonenumberlength = phonenumberlength
        self._load(addressbookfile)

    def _load(self, addressbookfile: str):
        vcards = vobject.readComponents(phonesystem.util.get_file(addressbookfile))
        for vcard in vcards:
            for child in vcard.getChildren():
                if child.name == "TEL":
                    self._phonenumbers[self._cleanphonenumber(child.value)] = child.value

    def _cleanphonenumber(self, number: str):
        clean_number = ''
        count = 0
        for c in number:
            if count == 0 and c == '+':
                clean_number += c
            elif c.isdigit():
                clean_number += c
            count = count + 1
        if not clean_number.startswith('+'):
            if len(clean_number) == self._phonenumberlength:
                clean_number = '+' + self._countrycode + clean_number
            else:
                clean_number = '+' + clean_number
        return clean_number

    def containsphonenumber(self, phonenumber: str):
        return self._cleanphonenumber(phonenumber) in self._phonenumbers

    @staticmethod
    def get_shared_instance(countrycode: str, phonenumberlength: int, addressbookfile: str):
        if addressbookfile not in AddressBook.__shared_instances:
            AddressBook.__shared_instances[addressbookfile] =\
                AddressBook(countrycode, phonenumberlength, addressbookfile)
        return AddressBook.__shared_instances[addressbookfile]
