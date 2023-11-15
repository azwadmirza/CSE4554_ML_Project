    def msg_curse(self, args=None):
        """Return the dict to display in the curse interface."""
        # Init the return message
        ret = []

        # Only process if stats exist and plugin not disabled
        if not self.stats or args.disable_load:
            return ret

        # Build the string message
        # Header
        msg = '{0:8}'.format('LOAD')
        ret.append(self.curse_add_line(msg, "TITLE"))
        # Core number
        if 'cpucore' in self.stats and self.stats['cpucore'] > 0:
            msg = '{0}-core'.format(int(self.stats['cpucore']))
            ret.append(self.curse_add_line(msg))
        # New line
        ret.append(self.curse_new_line())
        # 1min load
        msg = '{0:8}'.format('1 min:')
        ret.append(self.curse_add_line(msg))
        msg = '{0:>6.2f}'.format(self.stats['min1'])
        ret.append(self.curse_add_line(msg))
        # New line
        ret.append(self.curse_new_line())
        # 5min load
        msg = '{0:8}'.format('5 min:')
        ret.append(self.curse_add_line(msg))
        msg = '{0:>6.2f}'.format(self.stats['min5'])
        ret.append(self.curse_add_line(
            msg, self.get_views(key='min5', option='decoration')))
        # New line
        ret.append(self.curse_new_line())
        # 15min load
        msg = '{0:8}'.format('15 min:')
        ret.append(self.curse_add_line(msg))
        msg = '{0:>6.2f}'.format(self.stats['min15'])
        ret.append(self.curse_add_line(
            msg, self.get_views(key='min15', option='decoration')))

        return ret