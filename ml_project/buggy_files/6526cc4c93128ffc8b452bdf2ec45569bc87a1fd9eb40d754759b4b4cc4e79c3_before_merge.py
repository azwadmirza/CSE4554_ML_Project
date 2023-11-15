    def msg_curse(self, args=None):
        """Return the dict to display in the curse interface."""
        # Init the return message
        ret = []

        # Only process if stats exist and display plugin enable...
        if not self.stats or args.disable_ip:
            return ret

        # Build the string message
        msg = ' - '
        ret.append(self.curse_add_line(msg))
        msg = 'IP '
        ret.append(self.curse_add_line(msg, 'TITLE'))
        msg = '{0:}/{1}'.format(self.stats['address'], self.stats['mask_cidr'])
        ret.append(self.curse_add_line(msg))
        if self.stats['public_address'] is not None:
            msg = ' Pub '
            ret.append(self.curse_add_line(msg, 'TITLE'))
            msg = '{0:}'.format(self.stats['public_address'])
            ret.append(self.curse_add_line(msg))

        return ret