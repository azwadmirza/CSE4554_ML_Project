    def __init__(self, *args, **kwds):
        super(OSVERSIONINFO, self).__init__(*args, **kwds)
        self.dwOSVersionInfoSize = ctypes.sizeof(self)
        kernel32.GetVersionExW(ctypes.byref(self))