import logging

success_logger = logging.getLogger("patient_success")
success_logger.setLevel(logging.INFO)

error_logger = logging.getLogger("patient_errors")
error_logger.setLevel(logging.ERROR)

formatter = logging.Formatter("%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s")

success_handler = logging.FileHandler("good_log.txt", 'a', 'utf-8')

error_handler = logging.FileHandler("error_log.txt", 'a', 'utf-8')

success_handler.setFormatter(formatter)
error_handler.setFormatter(formatter)

success_logger.addHandler(success_handler)
error_logger.addHandler(error_handler)