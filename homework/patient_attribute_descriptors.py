import re
from collections.abc import Sized, Iterable

MIN_LENGTH_OF_PHONE_NUMBER = 11  # digits only, for 1-digit country codes
MAX_LENGTH_OF_PHONE_NUMBER = 14  # digits only, for 4-digit country codes


def sum_of_lens(iterable: Iterable):
    """Returns number of elements in 1/1.5/2 dim list"""
    return sum(map(lambda x: len(x) if isinstance(x, Sized) else 1, iterable))


class ModifyError(Exception):
    def __init__(self, text=None):
        self.txt = text


class NameNoModifyDescriptor:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if self.name in instance.__dict__:
            # Не уверен, что так стоит работать с персональными данными, но для примера пусть будет
            message = "Tried modifying {} of patient: {}".format(self.name, str(instance))
            instance.error_logger.error(message)
            raise ModifyError(message)

        if not isinstance(value, str):
            message = "Argument {} is not an instance of str".format(value)
            instance.error_logger.error(message)
            raise TypeError(message)

        if not value.isalpha():
            message = "Argument {} is in unsupported form".format(value)
            instance.error_logger.error(message)
            raise ValueError(message)

        instance.__dict__[self.name] = value.capitalize()
        instance.success_logger.info("{} assigned as {}".format(self.name, instance.__dict__[self.name]))


class DateDescriptor:
    @staticmethod
    def is_date(value: str):
        """Check if value follows format of date: yyyy/mm/dd for any regular separators"""

        if len(value) != 10:
            return False

        blocks = re.findall(r"[\w']+", value)

        if list(map(lambda x: len(x), blocks)) != [4, 2, 2]:
            return False

        for e in blocks:
            if not e.isdigit():
                return False

        return True

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if not isinstance(value, str):
            message = "Argument {} is not an instance of str".format(value)
            instance.error_logger.error(message)
            raise TypeError(message)

        if not self.is_date(value):
            message = "Argument {} is in unsupported form".format(value)
            instance.error_logger.error(message)
            raise ValueError(message)

        instance.__dict__[self.name] = value
        instance.success_logger.info("{} assigned as {}".format(self.name, instance.__dict__[self.name]))


class PhoneDescriptor:
    @staticmethod
    def is_phone_number(value: str):
        """Check if value contain number of digits from MIN_LENGTH_OF_PHONE_NUMBER to MAX_LENGTH_OF_PHONE_NUMBER"""

        blocks_of_digits = re.findall(r"[1-9]+", str(value))
        number_of_digits = sum_of_lens(blocks_of_digits)

        return MIN_LENGTH_OF_PHONE_NUMBER <= number_of_digits <= MAX_LENGTH_OF_PHONE_NUMBER

    @staticmethod
    def cast_phone_to_format(value: str):
        """Cast value to format    <code> ddd ddd dd dd
        <code> - country code from 1 digit up to 4"""
        value = re.sub(r"[\\ +._-]", "", value)

        code_len = len(value) - 10

        if code_len == 1 and value[0] == '8':
            value = '7' + value[0:]

        return ' '.join([value[0: code_len], value[code_len: code_len + 3],
                         value[code_len + 3: code_len + 6], value[code_len + 6: code_len + 8],
                         value[code_len + 8: code_len + 10], value[code_len + 10:]])

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        if type(value) != str:
            message = "Argument {} is not an instance of str".format(value)
            instance.error_logger.error(message)
            raise TypeError(message)

        if not self.is_phone_number(value):
            message = "Argument {} is in unsupported form".format(value)
            instance.error_logger.error(message)
            raise ValueError(message)

        instance.__dict__[self.name] = self.cast_phone_to_format(value)
        instance.success_logger.info("{} assigned as {}".format(self.name, instance.__dict__[self.name]))


class DocumentReadOnlyDescriptor:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__['_Patient__document'].__dict__[self.name]

    def __set__(self, instance, value):
        # Ибо менять тип не меняя номера - странно(да и наоборот иногда тоже)
        raise ModifyError("Use Patient.update_document(...) to update document information")


class DocumentTypeDescriptor:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        allowed_types = ["паспорт", "загран", "водительские права"]

        if not isinstance(value, str):
            message = "Argument {} is not an instance of str".format(value)
            instance.error_logger.error(message)
            raise TypeError(message)

        value = value.lower()

        if value not in allowed_types:
            message = "Argument {} is in unsupported form".format(value)
            instance.error_logger.error(message)
            raise ValueError(message)

        instance.__dict__[self.name] = value
        instance.success_logger.info("{} assigned as {}".format(self.name, instance.__dict__[self.name]))


def all_digits_to_str(value):
    """From iterable with digits and other stuff form string of only digits"""

    digits = ""
    for e in value:
        if e.isdigit():
            digits += e

    return digits


def cast_to_passport(number: str):
    """ Cast number with correct number of digits to PASSPORT_FORMAT = '0000 000000' """
    digits = all_digits_to_str(number)
    return ' '.join((digits[:4], digits[4:]))


def cast_to_international_passport(number: str):
    """ Cast number with correct number of digits to INTERNATIONAL_PASSPORT_FORMAT = '00 0000000' """
    digits = all_digits_to_str(number)
    return ' '.join((digits[:2], digits[2:]))


def cast_to_driver_licence(number: str):
    """ Cast number with correct number of digits to DRIVER_LICENSE_FORMAT = "00 00 000000" """
    digits = all_digits_to_str(number)
    return ' '.join((digits[:2], digits[2:4], digits[4:]))


def cast_to_document_type(number: str, document_type: str):
    """ Calls cast that fits type"""
    if document_type == "паспорт":
        return cast_to_passport(number)

    if document_type == "загран":
        return cast_to_international_passport(number)

    if document_type == "водительские права":
        return cast_to_driver_licence(number)


class DocumentIdDescriptor:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        types_len = {"паспорт": 10, "загран": 9, "водительские права": 10}  # Все по тестам
        document_type = instance.__dict__['document_type']

        blocks_of_digits = re.findall(r"[0-9]+", str(value))
        number_of_digits = sum_of_lens(blocks_of_digits)

        if types_len[document_type] != number_of_digits:
            message = "Argument {} is in unsupported form".format(value)
            instance.error_logger.error(message)
            raise ValueError(message)

        instance.__dict__[self.name] = cast_to_document_type(value, document_type)
        instance.success_logger.info("{} assigned as {}".format(self.name, instance.__dict__[self.name]))
