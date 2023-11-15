    def msg_curse(self, args=None, max_width=None):
        """Return the dict to display in the curse interface."""
        # Init the return message
        ret = []

        # Only process if stats exist and display plugin enable...
        if not self.stats or self.is_disable():
            return ret

        # Max size for the interface name
        name_max_width = max_width - 12

        # Header
        msg = '{:{width}}'.format('DISK I/O', width=name_max_width)
        ret.append(self.curse_add_line(msg, "TITLE"))
        if args.diskio_iops:
            msg = '{:>7}'.format('IOR/s')
            ret.append(self.curse_add_line(msg))
            msg = '{:>7}'.format('IOW/s')
            ret.append(self.curse_add_line(msg))
        else:
            msg = '{:>7}'.format('R/s')
            ret.append(self.curse_add_line(msg))
            msg = '{:>7}'.format('W/s')
            ret.append(self.curse_add_line(msg))
        # Disk list (sorted by name)
        for i in self.sorted_stats():
            # Is there an alias for the disk name ?
            disk_real_name = i['disk_name']
            disk_name = self.has_alias(i['disk_name'])
            if disk_name is None:
                disk_name = disk_real_name
            # New line
            ret.append(self.curse_new_line())
            if len(disk_name) > name_max_width:
                # Cut disk name if it is too long
                disk_name = '_' + disk_name[-name_max_width:]
            msg = '{:{width}}'.format(b(disk_name),
                                      width=name_max_width)
            ret.append(self.curse_add_line(msg))
            if args.diskio_iops:
                # count
                txps = self.auto_unit(
                    int(i['read_count'] // i['time_since_update']))
                rxps = self.auto_unit(
                    int(i['write_count'] // i['time_since_update']))
                msg = '{:>7}'.format(txps)
                ret.append(self.curse_add_line(msg,
                                               self.get_views(item=i[self.get_key()],
                                                              key='read_count',
                                                              option='decoration')))
                msg = '{:>7}'.format(rxps)
                ret.append(self.curse_add_line(msg,
                                               self.get_views(item=i[self.get_key()],
                                                              key='write_count',
                                                              option='decoration')))
            else:
                # Bitrate
                txps = self.auto_unit(
                    int(i['read_bytes'] // i['time_since_update']))
                rxps = self.auto_unit(
                    int(i['write_bytes'] // i['time_since_update']))
                msg = '{:>7}'.format(txps)
                ret.append(self.curse_add_line(msg,
                                               self.get_views(item=i[self.get_key()],
                                                              key='read_bytes',
                                                              option='decoration')))
                msg = '{:>7}'.format(rxps)
                ret.append(self.curse_add_line(msg,
                                               self.get_views(item=i[self.get_key()],
                                                              key='write_bytes',
                                                              option='decoration')))

        return ret