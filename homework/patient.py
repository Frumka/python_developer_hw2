from homework.patient_attribute_descriptors import *
import csv
from homework.patient_logger import *

CSV_LOG_NAME = 'patients.csv'


# class Document:
#     document_type: str
#     document_type = DocumentTypeDescriptor()
#
#     document_id: str
#     document_id = DocumentIdDescriptor()
#
#     def __init__(self, document_type, document_id):
#         self.success_logger = logging.getLogger("patient_success")
#         self.error_logger = logging.getLogger("patient_errors")
#
#         self.document_type = document_type
#         self.document_id = document_id


class Patient:
    first_name: str
    first_name = NameNoModifyDescriptor()

    last_name: str
    last_name = NameNoModifyDescriptor()

    birth_date: str
    birth_date = DateDescriptor()

    phone: str
    phone = PhoneDescriptor()

    document_type: str
    document_type = DocumentTypeDescriptor()

    document_id: str
    document_id = DocumentIdDescriptor()

    def __init__(self, first_name, last_name, birth_date, phone, document_type, document_id):
        self.success_logger = logging.getLogger("patient_success")
        self.error_logger = logging.getLogger("patient_errors")

        self.first_name = first_name
        self.last_name = last_name
        self.birth_date = birth_date
        self.phone = phone
        self.document_type = document_type
        self.document_id = document_id
        self.success_logger.info("Patient {} successfully created".format(self.first_name + ' ' + self.last_name))

    @staticmethod
    def create(first_name, last_name, birth_date, phone, document_type, document_id):
        return Patient(first_name, last_name, birth_date, phone, document_type, document_id)

    def __str__(self):
        return ', '.join([self.first_name, self.last_name, self.birth_date, self.phone,
                          self.document_type, self.document_id])

    def save(self):
        data = [self.first_name, self.last_name, self.birth_date, self.phone, self.document_type, self.document_id]

        try:
            with open(CSV_LOG_NAME, "a", newline="", encoding='utf-8') as file:
                csv.writer(file).writerow(data)

        except UnicodeError:
            message = 'Problem with encoding in file {}'.format(CSV_LOG_NAME)
            self.error_logger.error(message)
            raise UnicodeError(message)

        except PermissionError:
            message = "Permission required to write to file"
            self.error_logger.error(message)
            raise PermissionError(message)

        except RuntimeError:
            message = "Error in Runtime while saving patient"
            self.error_logger.error(message)
            raise RuntimeError(message)

        else:
            self.success_logger.info("Patient {} successfully saved".format(self.first_name + ' ' + self.last_name))

    def __del__(self):
        success_handler.close()
        error_handler.close()


class PatientCollection:
    def __init__(self, log_file_path, limit=-1):
        self.path = log_file_path
        self.line_byte_number = 0
        self.count = limit

    def __iter__(self):
        return self

    def __next__(self):
        with open(self.path, 'r', encoding='utf-8') as patients_csv:
            patients_csv.seek(self.line_byte_number)
            data = patients_csv.readline()
            self.line_byte_number = patients_csv.tell()

        if not data or self.count == 0:
            raise StopIteration

        self.count -= 1
        return Patient(*data.split(','))

    def limit(self, n):
        self.count = n
        return self.__iter__()
