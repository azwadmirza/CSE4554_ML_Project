    def __init__(self, message, **kwargs):
        command = ' '.join(sys.argv)
        super(CommandArgumentError, self).__init__(message, command=command, **kwargs)