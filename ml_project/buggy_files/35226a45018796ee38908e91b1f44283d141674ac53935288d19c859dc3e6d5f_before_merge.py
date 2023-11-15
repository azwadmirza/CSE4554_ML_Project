    def __init__(self, serial=''):
        self._serial = serial
        # logging.log_path only exists when this is used in an Mobly test run.
        self._log_path_base = getattr(logging, 'log_path', '/tmp/logs')
        self._log_path = os.path.join(self._log_path_base,
                                      'AndroidDevice%s' % self._serial)
        self._debug_tag = self._serial
        self.log = AndroidDeviceLoggerAdapter(logging.getLogger(), {
            'tag': self.debug_tag
        })
        self.sl4a = None
        self.ed = None
        self._adb_logcat_process = None
        self.adb_logcat_file_path = None
        self.adb = adb.AdbProxy(serial)
        self.fastboot = fastboot.FastbootProxy(serial)
        if not self.is_bootloader and self.is_rootable:
            self.root_adb()
        # A dict for tracking snippet clients. Keys are clients' attribute
        # names, values are the clients: {<attr name string>: <client object>}.
        self._snippet_clients = {}
        # Device info cache.
        self._user_added_device_info = {}