    def msg_curse(self, args=None, max_width=None):
        """Return the dict to display in the curse interface."""
        # Init the return message
        ret = []

        # Only process if stats exist and display plugin enable...
        if not self.stats or self.is_disable():
            return ret

        # Max size for the interface name
        name_max_width = max_width - 7

        # Header
        msg = '{:{width}}'.format('FOLDERS',
                                  width=name_max_width)
        ret.append(self.curse_add_line(msg, "TITLE"))

        # Data
        for i in self.stats:
            ret.append(self.curse_new_line())
            if len(i['path']) > name_max_width:
                # Cut path if it is too long
                path = '_' + i['path'][-name_max_width + 1:]
            else:
                path = i['path']
            msg = '{:{width}}'.format(b(path),
                                      width=name_max_width)
            ret.append(self.curse_add_line(msg))
            try:
                msg = '{:>9}'.format(self.auto_unit(i['size']))
            except (TypeError, ValueError):
                msg = '{:>9}'.format(i['size'])
            ret.append(self.curse_add_line(msg, self.get_alert(i)))

        return ret