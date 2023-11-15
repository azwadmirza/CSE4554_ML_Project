    def __init__(self, module):
        super(NosystemdTimezone, self).__init__(module)
        # Validate given timezone
        if 'name' in self.value:
            self._verify_timezone()
            self.update_timezone  = self.module.get_bin_path('cp', required=True)
            self.update_timezone += ' %s /etc/localtime' % tzfile
        self.update_hwclock = self.module.get_bin_path('hwclock', required=True)
        # Distribution-specific configurations
        if self.module.get_bin_path('dpkg-reconfigure') is not None:
            # Debian/Ubuntu
            self.update_timezone       = self.module.get_bin_path('dpkg-reconfigure', required=True)
            self.update_timezone      += ' --frontend noninteractive tzdata'
            self.conf_files['name']    = '/etc/timezone'
            self.conf_files['hwclock'] = '/etc/default/rcS'
            self.regexps['name']       = re.compile(r'^([^\s]+)', re.MULTILINE)
            self.tzline_format         = '%s\n'
        else:
            # RHEL/CentOS
            if self.module.get_bin_path('tzdata-update') is not None:
                self.update_timezone   = self.module.get_bin_path('tzdata-update', required=True)
            # else:
            #   self.update_timezone   = 'cp ...' <- configured above
            self.conf_files['name']    = '/etc/sysconfig/clock'
            self.conf_files['hwclock'] = '/etc/sysconfig/clock'
            self.regexps['name']       = re.compile(r'^ZONE\s*=\s*"?([^"\s]+)"?', re.MULTILINE)
            self.tzline_format         = 'ZONE="%s"\n'
        self.update_hwclock  = self.module.get_bin_path('hwclock', required=True)