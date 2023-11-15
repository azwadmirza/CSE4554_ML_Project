    def msg_curse(self, args=None):
        """Return the dict to display in the curse interface."""
        # Init the return message
        ret = []

        # Only process if stats exist and display plugin enable...
        if not self.stats or args.disable_sensors:
            return ret

        # Build the string message
        # Header
        msg = '{0:18}'.format('SENSORS')
        ret.append(self.curse_add_line(msg, "TITLE"))

        for i in self.stats:
            # New line
            ret.append(self.curse_new_line())
            # Alias for the lable name ?
            label = self.has_alias(i['label'].lower())
            if label is None:
                label = i['label']
            if i['type'] != 'fan_speed':
                msg = '{0:15}'.format(label[:15])
            else:
                msg = '{0:13}'.format(label[:13])
            ret.append(self.curse_add_line(msg))
            # Temperature could be 'ERR' or 'SLP' (see issue#824)
            if i['value'] in (b'ERR', b'SLP'):
                msg = '{0:>8}'.format(i['value'])
                ret.append(self.curse_add_line(
                    msg, self.get_views(item=i[self.get_key()],
                                        key='value',
                                        option='decoration')))
            else:
                if (args.fahrenheit and i['type'] != 'battery' and
                        i['type'] != 'fan_speed'):
                    value = to_fahrenheit(i['value'])
                    unit = 'F'
                else:
                    value = i['value']
                    unit = i['unit']
                try:
                    msg = '{0:>7.0f}{1}'.format(value, unit)
                    ret.append(self.curse_add_line(
                        msg, self.get_views(item=i[self.get_key()],
                                            key='value',
                                            option='decoration')))
                except (TypeError, ValueError):
                    pass

        return ret