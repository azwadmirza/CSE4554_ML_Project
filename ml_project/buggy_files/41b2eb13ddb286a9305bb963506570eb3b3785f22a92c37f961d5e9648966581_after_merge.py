    def nice_get(self):
        # Note #1: getpriority(3) doesn't work for realtime processes.
        # Psinfo is what ps uses, see:
        # https://github.com/giampaolo/psutil/issues/1194
        return self._proc_basic_info()[proc_info_map['nice']]