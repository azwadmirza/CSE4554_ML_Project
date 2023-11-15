    def get_process_curses_data(self, p, first, args):
        """Get curses data to display for a process.

        - p is the process to display
        - first is a tag=True if the process is the first on the list
        """
        ret = [self.curse_new_line()]
        # CPU
        if 'cpu_percent' in p and p['cpu_percent'] is not None and p['cpu_percent'] != '':
            if args.disable_irix and self.nb_log_core != 0:
                msg = '{:>6.1f}'.format(p['cpu_percent'] / float(self.nb_log_core))
            else:
                msg = '{:>6.1f}'.format(p['cpu_percent'])
            alert = self.get_alert(p['cpu_percent'],
                                   highlight_zero=False,
                                   is_max=(p['cpu_percent'] == self.max_values['cpu_percent']),
                                   header="cpu")
            ret.append(self.curse_add_line(msg, alert))
        else:
            msg = '{:>6}'.format('?')
            ret.append(self.curse_add_line(msg))
        # MEM
        if 'memory_percent' in p and p['memory_percent'] is not None and p['memory_percent'] != '':
            msg = '{:>6.1f}'.format(p['memory_percent'])
            alert = self.get_alert(p['memory_percent'],
                                   highlight_zero=False,
                                   is_max=(p['memory_percent'] == self.max_values['memory_percent']),
                                   header="mem")
            ret.append(self.curse_add_line(msg, alert))
        else:
            msg = '{:>6}'.format('?')
            ret.append(self.curse_add_line(msg))
        # VMS/RSS
        if 'memory_info' in p and p['memory_info'] is not None and p['memory_info'] != '':
            # VMS
            msg = '{:>6}'.format(self.auto_unit(p['memory_info'][1], low_precision=False))
            ret.append(self.curse_add_line(msg, optional=True))
            # RSS
            msg = '{:>6}'.format(self.auto_unit(p['memory_info'][0], low_precision=False))
            ret.append(self.curse_add_line(msg, optional=True))
        else:
            msg = '{:>6}'.format('?')
            ret.append(self.curse_add_line(msg))
            ret.append(self.curse_add_line(msg))
        # PID
        msg = '{:>{width}}'.format(p['pid'], width=self.__max_pid_size() + 1)
        ret.append(self.curse_add_line(msg))
        # USER
        if 'username' in p:
            # docker internal users are displayed as ints only, therefore str()
            # Correct issue #886 on Windows OS
            msg = ' {:9}'.format(str(p['username'])[:9])
            ret.append(self.curse_add_line(msg))
        else:
            msg = ' {:9}'.format('?')
            ret.append(self.curse_add_line(msg))
        # NICE
        if 'nice' in p:
            nice = p['nice']
            if nice is None:
                nice = '?'
            msg = '{:>5}'.format(nice)
            ret.append(self.curse_add_line(msg,
                                           decoration=self.get_nice_alert(nice)))
        else:
            msg = '{:>5}'.format('?')
            ret.append(self.curse_add_line(msg))
        # STATUS
        if 'status' in p:
            status = p['status']
            msg = '{:>2}'.format(status)
            if status == 'R':
                ret.append(self.curse_add_line(msg, decoration='STATUS'))
            else:
                ret.append(self.curse_add_line(msg))
        else:
            msg = '{:>2}'.format('?')
            ret.append(self.curse_add_line(msg))
        # TIME+
        try:
            delta = timedelta(seconds=sum(p['cpu_times']))
        except (OverflowError, TypeError) as e:
            # Catch OverflowError on some Amazon EC2 server
            # See https://github.com/nicolargo/glances/issues/87
            # Also catch TypeError on macOS
            # See: https://github.com/nicolargo/glances/issues/622
            # logger.debug("Cannot get TIME+ ({})".format(e))
            msg = '{:>10}'.format('?')
        else:
            hours, minutes, seconds, microseconds = convert_timedelta(delta)
            if hours:
                msg = '{:>4}h'.format(hours)
                ret.append(self.curse_add_line(msg, decoration='CPU_TIME', optional=True))
                msg = '{}:{}'.format(str(minutes).zfill(2), seconds)
            else:
                msg = '{:>4}:{}.{}'.format(minutes, seconds, microseconds)
        ret.append(self.curse_add_line(msg, optional=True))
        # IO read/write
        if 'io_counters' in p and p['io_counters'][4] == 1 and p['time_since_update'] != 0:
            # Display rate if stats is available and io_tag ([4]) == 1
            # IO read
            io_rs = int((p['io_counters'][0] - p['io_counters'][2]) / p['time_since_update'])
            if io_rs == 0:
                msg = '{:>6}'.format("0")
            else:
                msg = '{:>6}'.format(self.auto_unit(io_rs, low_precision=True))
            ret.append(self.curse_add_line(msg, optional=True, additional=True))
            # IO write
            io_ws = int((p['io_counters'][1] - p['io_counters'][3]) / p['time_since_update'])
            if io_ws == 0:
                msg = '{:>6}'.format("0")
            else:
                msg = '{:>6}'.format(self.auto_unit(io_ws, low_precision=True))
            ret.append(self.curse_add_line(msg, optional=True, additional=True))
        else:
            msg = '{:>6}'.format("?")
            ret.append(self.curse_add_line(msg, optional=True, additional=True))
            ret.append(self.curse_add_line(msg, optional=True, additional=True))

        # Command line
        # If no command line for the process is available, fallback to
        # the bare process name instead
        cmdline = p['cmdline']
        try:
            if cmdline:
                path, cmd, arguments = split_cmdline(cmdline)
                if os.path.isdir(path) and not args.process_short_name:
                    msg = ' {}'.format(path) + os.sep
                    ret.append(self.curse_add_line(msg, splittable=True))
                    ret.append(self.curse_add_line(cmd, decoration='PROCESS', splittable=True))
                else:
                    msg = ' {}'.format(cmd)
                    ret.append(self.curse_add_line(msg, decoration='PROCESS', splittable=True))
                if arguments:
                    msg = ' {}'.format(arguments)
                    ret.append(self.curse_add_line(msg, splittable=True))
            else:
                msg = ' {}'.format(p['name'])
                ret.append(self.curse_add_line(msg, splittable=True))
        except UnicodeEncodeError:
            ret.append(self.curse_add_line('', splittable=True))

        # Add extended stats but only for the top processes
        if first and 'extended_stats' in p:
            # Left padding
            xpad = ' ' * 13
            # First line is CPU affinity
            if 'cpu_affinity' in p and p['cpu_affinity'] is not None:
                ret.append(self.curse_new_line())
                msg = xpad + 'CPU affinity: ' + str(len(p['cpu_affinity'])) + ' cores'
                ret.append(self.curse_add_line(msg, splittable=True))
            # Second line is memory info
            if 'memory_info' in p and p['memory_info'] is not None:
                ret.append(self.curse_new_line())
                msg = xpad + 'Memory info: '
                for k, v in iteritems(p['memory_info']._asdict()):
                    # Ignore rss and vms (already displayed)
                    if k not in ['rss', 'vms'] and v is not None:
                        msg += self.auto_unit(v, low_precision=False) + ' ' + k + ' '
                if 'memory_swap' in p and p['memory_swap'] is not None:
                    msg += self.auto_unit(p['memory_swap'], low_precision=False) + ' swap '
                ret.append(self.curse_add_line(msg, splittable=True))
            # Third line is for open files/network sessions
            msg = ''
            if 'num_threads' in p and p['num_threads'] is not None:
                msg += str(p['num_threads']) + ' threads '
            if 'num_fds' in p and p['num_fds'] is not None:
                msg += str(p['num_fds']) + ' files '
            if 'num_handles' in p and p['num_handles'] is not None:
                msg += str(p['num_handles']) + ' handles '
            if 'tcp' in p and p['tcp'] is not None:
                msg += str(p['tcp']) + ' TCP '
            if 'udp' in p and p['udp'] is not None:
                msg += str(p['udp']) + ' UDP'
            if msg != '':
                ret.append(self.curse_new_line())
                msg = xpad + 'Open: ' + msg
                ret.append(self.curse_add_line(msg, splittable=True))
            # Fouth line is IO nice level (only Linux and Windows OS)
            if 'ionice' in p and p['ionice'] is not None:
                ret.append(self.curse_new_line())
                msg = xpad + 'IO nice: '
                k = 'Class is '
                v = p['ionice'].ioclass
                # Linux: The scheduling class. 0 for none, 1 for real time, 2 for best-effort, 3 for idle.
                # Windows: On Windows only ioclass is used and it can be set to 2 (normal), 1 (low) or 0 (very low).
                if WINDOWS:
                    if v == 0:
                        msg += k + 'Very Low'
                    elif v == 1:
                        msg += k + 'Low'
                    elif v == 2:
                        msg += 'No specific I/O priority'
                    else:
                        msg += k + str(v)
                else:
                    if v == 0:
                        msg += 'No specific I/O priority'
                    elif v == 1:
                        msg += k + 'Real Time'
                    elif v == 2:
                        msg += k + 'Best Effort'
                    elif v == 3:
                        msg += k + 'IDLE'
                    else:
                        msg += k + str(v)
                #  value is a number which goes from 0 to 7.
                # The higher the value, the lower the I/O priority of the process.
                if hasattr(p['ionice'], 'value') and p['ionice'].value != 0:
                    msg += ' (value %s/7)' % str(p['ionice'].value)
                ret.append(self.curse_add_line(msg, splittable=True))

        return ret