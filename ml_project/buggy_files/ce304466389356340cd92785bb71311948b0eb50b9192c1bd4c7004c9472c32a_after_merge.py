    def msg_curse(self, args=None):
        """Return the dict to display in the curse interface."""
        # Init the return message
        ret = []

        # Only process if stats exist and display plugin enable...
        if not self.stats or args.disable_raid:
            return ret

        # Build the string message
        # Header
        msg = '{0:11}'.format('RAID disks')
        ret.append(self.curse_add_line(msg, "TITLE"))
        msg = '{0:>6}'.format('Used')
        ret.append(self.curse_add_line(msg))
        msg = '{0:>6}'.format('Avail')
        ret.append(self.curse_add_line(msg))
        # Data
        arrays = sorted(iterkeys(self.stats))
        for array in arrays:
            # New line
            ret.append(self.curse_new_line())
            # Display the current status
            status = self.raid_alert(self.stats[array]['status'], self.stats[array]['used'], self.stats[array]['available'])
            # Data: RAID type name | disk used | disk available
            array_type = self.stats[array]['type'].upper() if self.stats[array]['type'] is not None else 'UNKNOWN'
            msg = '{0:<5}{1:>6}'.format(array_type, array)
            ret.append(self.curse_add_line(msg))
            if self.stats[array]['status'] == 'active':
                msg = '{0:>6}'.format(self.stats[array]['used'])
                ret.append(self.curse_add_line(msg, status))
                msg = '{0:>6}'.format(self.stats[array]['available'])
                ret.append(self.curse_add_line(msg, status))
            elif self.stats[array]['status'] == 'inactive':
                ret.append(self.curse_new_line())
                msg = '└─ Status {0}'.format(self.stats[array]['status'])
                ret.append(self.curse_add_line(msg, status))
                components = sorted(iterkeys(self.stats[array]['components']))
                for i, component in enumerate(components):
                    if i == len(components) - 1:
                        tree_char = '└─'
                    else:
                        tree_char = '├─'
                    ret.append(self.curse_new_line())
                    msg = '   {0} disk {1}: '.format(tree_char, self.stats[array]['components'][component])
                    ret.append(self.curse_add_line(msg))
                    msg = '{0}'.format(component)
                    ret.append(self.curse_add_line(msg))
            if self.stats[array]['used'] < self.stats[array]['available']:
                # Display current array configuration
                ret.append(self.curse_new_line())
                msg = '└─ Degraded mode'
                ret.append(self.curse_add_line(msg, status))
                if len(self.stats[array]['config']) < 17:
                    ret.append(self.curse_new_line())
                    msg = '   └─ {0}'.format(self.stats[array]['config'].replace('_', 'A'))
                    ret.append(self.curse_add_line(msg))

        return ret