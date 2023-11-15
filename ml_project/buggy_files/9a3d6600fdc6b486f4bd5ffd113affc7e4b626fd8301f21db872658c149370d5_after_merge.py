    def msg_curse(self, args=None, max_width=None):
        """Return the dict to display in the curse interface."""
        # Init the return message
        ret = []

        # Only process if stats exist, not empty (issue #871) and plugin not disabled
        if not self.stats or (self.stats == []) or self.is_disable():
            return ret

        # Check if all GPU have the same name
        same_name = all(s['name'] == self.stats[0]['name'] for s in self.stats)

        # gpu_stats contain the first GPU in the list
        gpu_stats = self.stats[0]

        # Header
        header = ''
        if len(self.stats) > 1:
            header += '{} '.format(len(self.stats))
        if same_name:
            header += '{} {}'.format('GPU', gpu_stats['name'])
        else:
            header += '{}'.format('GPU')
        msg = header[:17]
        ret.append(self.curse_add_line(msg, "TITLE"))

        # Build the string message
        if len(self.stats) == 1 or args.meangpu:
            # GPU stat summary or mono GPU
            # New line
            ret.append(self.curse_new_line())
            # GPU PROC
            try:
                mean_proc = sum(s['proc'] for s in self.stats if s is not None) / len(self.stats)
            except TypeError:
                mean_proc_msg = '{:>4}'.format('N/A')
            else:
                mean_proc_msg = '{:>3.0f}%'.format(mean_proc)
            if len(self.stats) > 1:
                msg = '{:13}'.format('proc mean:')
            else:
                msg = '{:13}'.format('proc:')
            ret.append(self.curse_add_line(msg))
            ret.append(self.curse_add_line(
                mean_proc_msg, self.get_views(item=gpu_stats[self.get_key()],
                                              key='proc',
                                              option='decoration')))
            # New line
            ret.append(self.curse_new_line())
            # GPU MEM
            try:
                mean_mem = sum(s['mem'] for s in self.stats if s is not None) / len(self.stats)
            except TypeError:
                mean_mem_msg = '{:>4}'.format('N/A')
            else:
                mean_mem_msg = '{:>3.0f}%'.format(mean_mem)
            if len(self.stats) > 1:
                msg = '{:13}'.format('mem mean:')
            else:
                msg = '{:13}'.format('mem:')
            ret.append(self.curse_add_line(msg))
            ret.append(self.curse_add_line(
                mean_mem_msg, self.get_views(item=gpu_stats[self.get_key()],
                                             key='mem',
                                             option='decoration')))
            # New line
            ret.append(self.curse_new_line())
            # GPU TEMPERATURE
            try:
                mean_temperature = sum(s['temperature'] for s in self.stats if s is not None) / len(self.stats)
            except TypeError:
                mean_temperature_msg = '{:>4}'.format('N/A')
            else:
                unit = 'C'
                if args.fahrenheit:
                    mean_temperature = to_fahrenheit(mean_temperature)
                    unit = 'F'
                mean_temperature_msg = '{:>3.0f}{}'.format(mean_temperature,
                                                           unit)
            if len(self.stats) > 1:
                msg = '{:13}'.format('temp mean:')
            else:
                msg = '{:13}'.format('temperature:')
            ret.append(self.curse_add_line(msg))
            ret.append(self.curse_add_line(
                mean_temperature_msg, self.get_views(item=gpu_stats[self.get_key()],
                                                     key='temperature',
                                                     option='decoration')))
        else:
            # Multi GPU
            # Temperature is not displayed in this mode...
            for gpu_stats in self.stats:
                # New line
                ret.append(self.curse_new_line())
                # GPU ID + PROC + MEM + TEMPERATURE
                id_msg = '{}'.format(gpu_stats['gpu_id'])
                try:
                    proc_msg = '{:>3.0f}%'.format(gpu_stats['proc'])
                except (ValueError, TypeError):
                    proc_msg = '{:>4}'.format('N/A')
                try:
                    mem_msg = '{:>3.0f}%'.format(gpu_stats['mem'])
                except (ValueError, TypeError):
                    mem_msg = '{:>4}'.format('N/A')
                msg = '{}: {} mem: {}'.format(id_msg,
                                              proc_msg,
                                              mem_msg)
                ret.append(self.curse_add_line(msg))

        return ret