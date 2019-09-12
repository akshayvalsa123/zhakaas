class TSAdminException(Exception):
    pass

class ImportException(TSAdminException):
    """Custom Exception for Import related errors.
    """
    def __init__(self, statusCode, message):
        self.statusCode = statusCode
        self.message = message

class LeadException(TSAdminException):
    """Custom Exception for Lead related errors.
    """
    def __init__(self, statusCode, message):
        self.statusCode = statusCode
        self.message = message

class ReportException(TSAdminException):
    """Custom Exception for Report related errors.
    """
    def __init__(self, statusCode, message):
        self.statusCode = statusCode
        self.message = message

class LoginException(TSAdminException):
    """Custom Exception for Login related errors.
    """
    def __init__(self, statusCode, message):
        self.statusCode = statusCode
        self.message = message

class LogoutException(TSAdminException):
    """Custom Exception for Logout related errors.
    """
    def __init__(self, statusCode, message):
        self.statusCode = statusCode
        self.message = message

class SyncException(TSAdminException):
    """Custom Exception for Sync related errors.
    """
    def __init__(self, statusCode, message):
        self.statusCode = statusCode
        self.message = message

class DeviceSaveException(TSAdminException):
    """Custom Exception for Device save  related errors.
    """
    def __init__(self, statusCode, message):
        self.statusCode = statusCode
        self.message = message
