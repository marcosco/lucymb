class ErrorReadingDevice(Exception):
    def __init__(self, message):
        self.msg = message
        # Return control to super class
        super(Exception, self).__init__(message)


class DeviceNotFound(Exception):
    def __init__(self, message):
        self.msg = message
        # Return control to super class
        super(Exception, self).__init__(message)


class InvalidOperation(Exception):
    def __init__(self, message):
        self.msg = message
        # Return control to super class
        super(Exception, self).__init__(message)


class NoTypeSpecifiedToFactory(Exception):
    def __init__(self, message):
        self.msg = message
        # Return control to super class
        super(Exception, self).__init__(message)
