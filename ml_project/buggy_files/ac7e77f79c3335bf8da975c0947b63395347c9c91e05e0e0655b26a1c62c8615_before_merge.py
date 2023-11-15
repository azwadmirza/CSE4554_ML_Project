    def __init__(self, command):
        message = "Conda could not find the command: '%(command)s'"
        super(CommandNotFoundError, self).__init__(message, command=command)