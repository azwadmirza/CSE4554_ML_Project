        def __init__(self, dialect, connection, checkfirst=False, **kwargs):
            super(ENUM.EnumDropper, self).__init__(connection, **kwargs)
            self.checkfirst = checkfirst