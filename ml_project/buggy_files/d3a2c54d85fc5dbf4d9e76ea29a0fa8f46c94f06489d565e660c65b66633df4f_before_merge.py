    def msg_curse(self, args=None):
        """Return the dict to display in the curse interface."""
        # Init the return message
        ret = []

        # Only process if stats exist (and non null) and display plugin enable...
        if not self.stats or args.disable_docker or len(self.stats['containers']) == 0:
            return ret

        # Build the string message
        # Title
        msg = '{0}'.format('CONTAINERS')
        ret.append(self.curse_add_line(msg, "TITLE"))
        msg = ' {0}'.format(len(self.stats['containers']))
        ret.append(self.curse_add_line(msg))
        msg = ' ({0} {1})'.format('served by Docker',
                                  self.stats['version']["Version"])
        ret.append(self.curse_add_line(msg))
        ret.append(self.curse_new_line())
        # Header
        ret.append(self.curse_new_line())
        # msg = '{0:>14}'.format('Id')
        # ret.append(self.curse_add_line(msg))
        # Get the maximum containers name (cutted to 20 char max)
        name_max_width = min(20, len(max(self.stats['containers'], key=lambda x: len(x['name']))['name']))
        msg = ' {0:{width}}'.format('Name', width=name_max_width)
        ret.append(self.curse_add_line(msg))
        msg = '{0:>26}'.format('Status')
        ret.append(self.curse_add_line(msg))
        msg = '{0:>6}'.format('CPU%')
        ret.append(self.curse_add_line(msg))
        msg = '{0:>7}'.format('MEM')
        ret.append(self.curse_add_line(msg))
        msg = '{0:>6}'.format('IOR/s')
        ret.append(self.curse_add_line(msg))
        msg = '{0:>6}'.format('IOW/s')
        ret.append(self.curse_add_line(msg))
        msg = '{0:>6}'.format('Rx/s')
        ret.append(self.curse_add_line(msg))
        msg = '{0:>6}'.format('Tx/s')
        ret.append(self.curse_add_line(msg))
        msg = ' {0:8}'.format('Command')
        ret.append(self.curse_add_line(msg))
        # Data
        for container in self.stats['containers']:
            ret.append(self.curse_new_line())
            # Id
            # msg = '{0:>14}'.format(container['Id'][0:12])
            # ret.append(self.curse_add_line(msg))
            # Name
            name = container['name']
            if len(name) > name_max_width:
                name = '_' + name[-name_max_width + 1:]
            else:
                name = name[:name_max_width]
            msg = ' {0:{width}}'.format(name, width=name_max_width)
            ret.append(self.curse_add_line(msg))
            # Status
            status = self.container_alert(container['Status'])
            msg = container['Status'].replace("minute", "min")
            msg = '{0:>26}'.format(msg[0:25])
            ret.append(self.curse_add_line(msg, status))
            # CPU
            try:
                msg = '{0:>6.1f}'.format(container['cpu']['total'])
            except KeyError:
                msg = '{0:>6}'.format('?')
            ret.append(self.curse_add_line(msg))
            # MEM
            try:
                msg = '{0:>7}'.format(self.auto_unit(container['memory']['usage']))
            except KeyError:
                msg = '{0:>7}'.format('?')
            ret.append(self.curse_add_line(msg))
            # IO R/W
            for r in ['ior', 'iow']:
                try:
                    value = self.auto_unit(int(container['io'][r] // container['io']['time_since_update'] * 8)) + "b"
                    msg = '{0:>6}'.format(value)
                except KeyError:
                    msg = '{0:>6}'.format('?')
                ret.append(self.curse_add_line(msg))
            # NET RX/TX
            for r in ['rx', 'tx']:
                try:
                    value = self.auto_unit(int(container['network'][r] // container['network']['time_since_update'] * 8)) + "b"
                    msg = '{0:>6}'.format(value)
                except KeyError:
                    msg = '{0:>6}'.format('?')
                ret.append(self.curse_add_line(msg))
            # Command
            msg = ' {0}'.format(container['Command'])
            ret.append(self.curse_add_line(msg, splittable=True))

        return ret