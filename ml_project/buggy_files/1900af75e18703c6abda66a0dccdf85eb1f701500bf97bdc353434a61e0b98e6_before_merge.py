    def msg_curse(self, args=None):
        """Return the dict to display in the curse interface."""
        # Init the return message
        ret = []

        # No per CPU stat ? Exit...
        if not self.stats:
            msg = 'PER CPU not available'
            ret.append(self.curse_add_line(msg, "TITLE"))
            return ret

        # Build the string message
        # Header
        msg = '{:8}'.format('PER CPU')
        ret.append(self.curse_add_line(msg, "TITLE"))

        # Total per-CPU usage
        for cpu in self.stats:
            msg = '{:>6}%'.format(cpu['total'])
            ret.append(self.curse_add_line(msg))

        # Stats per-CPU
        for stat in ['user', 'system', 'idle', 'iowait', 'steal']:
            if stat not in self.stats[0]:
                continue

            ret.append(self.curse_new_line())
            msg = '{:8}'.format(stat + ':')
            ret.append(self.curse_add_line(msg))
            for cpu in self.stats:
                msg = '{:>6}%'.format(cpu[stat])
                ret.append(self.curse_add_line(msg,
                                               self.get_alert(cpu[stat], header=stat)))

        # Return the message with decoration
        return ret