    def msg_curse(self, args=None, max_width=None):
        """Return the dict to display in the curse interface."""
        # Init the return message
        ret = []

        # Only process if stats exist...
        if import_error_tag or not self.stats or self.is_disable():
            return ret

        # Max size for the interface name
        name_max_width = max_width - 6

        # Header
        msg = '{:{width}}'.format('SMART disks',
                                  width=name_max_width)
        ret.append(self.curse_add_line(msg, "TITLE"))
        # Data
        for device_stat in self.stats:
            # New line
            ret.append(self.curse_new_line())
            msg = '{:{width}}'.format(device_stat['DeviceName'][:max_width],
                                      width=max_width)
            ret.append(self.curse_add_line(msg))
            for smart_stat in sorted([i for i in device_stat.keys() if i != 'DeviceName'], key=int):
                ret.append(self.curse_new_line())
                msg = ' {:{width}}'.format(device_stat[smart_stat]['name'][:name_max_width-1].replace('_', ' '),
                                          width=name_max_width-1)
                ret.append(self.curse_add_line(msg))
                msg = '{:>8}'.format(device_stat[smart_stat]['raw'])
                ret.append(self.curse_add_line(msg))

        return ret