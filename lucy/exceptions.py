class ErrorReadingDevice(Exception):
    def __init__(self, message):
        self.msg = message
	super(Exception, self).__init__(message)

class DeviceNotFound(Exception):
    def __init__(self, message):
        self.msg = message
	super(Exception, self).__init__(message)

class InvalidOperation(Exception):
    def __init__(self, message):
        self.msg = message
	super(Exception, self).__init__(message)
