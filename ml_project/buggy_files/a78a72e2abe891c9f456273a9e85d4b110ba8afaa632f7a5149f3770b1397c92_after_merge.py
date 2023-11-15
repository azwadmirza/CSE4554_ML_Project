    def displayProcess(self, processcount, processlist, sortedby='',
                       log_count=0, core=1, cs_status="None"):
        """
        Display the processese:
        * summary
        * monitored processes list (optionnal)
        * processes detailed list
        cs_status:
            "None": standalone or server mode
            "Connected": Client is connected to the server
            "Disconnected": Client is disconnected from the server
        """
        # Process
        if not processcount:
            return 0
        screen_x = self.screen.getmaxyx()[1]
        screen_y = self.screen.getmaxyx()[0]
        # If there is no network & diskio & fs & sensors stats & hddtemp stats
        # then increase process window
        if (not self.network_tag and
            not self.diskio_tag and
            not self.fs_tag and
            not self.sensors_tag and
            not self.hddtemp_tag):
            process_x = 0
        else:
            process_x = self.process_x

        #******************
        # Processes summary
        #******************
        if not self.process_tag:
            self.term_window.addnstr(self.process_y, process_x,
                                     _("Processes (disabled)"),
                                     20, self.title_color if self.hascolors else
                                     curses.A_UNDERLINE)
            return 0
        if screen_y > self.process_y + 4 and screen_x > process_x + 48:
            # Compute others processes
            other = (processcount['total'] -
                     stats.getProcessCount()['running'] -
                     stats.getProcessCount()['sleeping'])
            # Thread is only available in Glances 1.7.4 or higher
            try:
                thread = processcount['thread']
            except KeyError:
                thread = '?'
            # Display the summary
            self.term_window.addnstr(self.process_y, process_x, _("Tasks"),
                                     9, self.title_color if self.hascolors else
                                     curses.A_UNDERLINE)
            self.term_window.addnstr(
                self.process_y, process_x + 8,
                '{0:>3} ({1:>3} {2}), {3:>2} {4}, {5:>3} {6}, {7:>2} {8}'.format(
                    str(processcount['total']),
                    str(thread),
                    _("thr"),
                    str(processcount['running']),
                    _("run"),
                    str(processcount['sleeping']),
                    _("slp"),
                    str(other),
                    _("oth")), 42)

        # Sort info
        # self.getProcessSortedBy() -> User sort choice
        #                  sortedby -> System last sort
        if self.getProcessSortedBy() == 'auto':
            sortmsg = _("sorted automatically")
        else:
            sortmsg = _("sorted by ") + sortedby
        if (screen_y > self.process_y + 4 and
            screen_x > process_x + 49 + len(sortmsg)):
            self.term_window.addnstr(self.process_y, 76, sortmsg, len(sortmsg))

        #*************************
        # Monitored processes list
        #*************************
        monitor_y = self.process_y
        if (len(monitors) > 0 and
            screen_y > self.process_y + 5 + len(monitors) and
            screen_x > process_x + 49):
            # Add space between process summary and monitored processes list
            monitor_y += 1
            item = 0
            for processes in monitors:
                # Display the monitored processes list (one line per monitored processes)
                monitor_y += 1
                # Search monitored processes by a regular expression
                monitoredlist = [p for p in processlist if re.search(monitors.regex(item), p['cmdline']) is not None]
                # Build and print non optional message
                monitormsg1 = "{0:>16} {1:3} {2:13}".format(
                    monitors.description(item)[0:15],
                    len(monitoredlist) if len(monitoredlist) > 1 else "",
                    _("RUNNING") if len(monitoredlist) > 0 else _("NOT RUNNING"))
                self.term_window.addnstr(monitor_y, self.process_x,
                                         monitormsg1, screen_x - process_x,
                                         self.__getMonitoredColor(len(monitoredlist),
                                                                  monitors.countmin(item),
                                                                  monitors.countmax(item)))
                # Build and print optional message
                if len(monitoredlist) > 0:
                    if (cs_status.lower() == "none" and
                        monitors.command(item) is not None):
                        # Execute the user command line
                        try:
                            cmdret = subprocess.check_output(monitors.command(item), shell=True)
                        except subprocess.CalledProcessError:
                            cmdret = _("Error: ") + monitors.command(item)
                        except Exception:
                            cmdret = _("Cannot execute command")
                    else:
                        # By default display CPU and MEM %
                        cmdret = "CPU: {0:.1f}% / MEM: {1:.1f}%".format(
                            sum([p['cpu_percent'] for p in monitoredlist]),
                            sum([p['memory_percent'] for p in monitoredlist]))
                else:
                    cmdret = ""
                    # cmdret = "{0} / {1} / {2}".format(len(monitoredlist),
                    #                                   monitors.countmin(item),
                    #                                   monitors.countmax(item))

                monitormsg2 = "{0}".format(cmdret)
                self.term_window.addnstr(monitor_y, self.process_x + 35,
                                         monitormsg2, screen_x - process_x - 35)

                # Generate log
                logs.add(self.__getMonitoredAlert(len(monitoredlist),
                                                  monitors.countmin(item),
                                                  monitors.countmax(item)),
                         "MON_" + str(item + 1),
                         len(monitoredlist),
                         proc_list=monitoredlist,
                         proc_desc=monitors.description(item))

                # Next...
                item += 1

        #*****************
        # Processes detail
        #*****************
        if screen_y > monitor_y + 4 and screen_x > process_x + 49:
            tag_pid = False
            tag_uid = False
            tag_nice = False
            tag_status = False
            tag_proc_time = False
            tag_io = False
            # tag_tcpudp = False

            if screen_x > process_x + 55:
                tag_pid = True
            if screen_x > process_x + 64:
                tag_uid = True
            if screen_x > process_x + 70:
                tag_nice = True
            if screen_x > process_x + 74:
                tag_status = True
            if screen_x > process_x + 77:
                tag_proc_time = True
            if screen_x > process_x + 92:
                tag_io = True
            if not psutil_get_io_counter_tag:
                tag_io = False
            # if screen_x > process_x + 107:
            #     tag_tcpudp = True

            # VMS
            self.term_window.addnstr(
                monitor_y + 2, process_x,
                format(_("VIRT"), '>5'), 5)
            # RSS
            self.term_window.addnstr(
                monitor_y + 2, process_x + 6,
                format(_("RES"), '>5'), 5)
            # CPU%
            self.term_window.addnstr(
                monitor_y + 2, process_x + 12,
                format(_("CPU%"), '>5'), 5,
                self.getProcessColumnColor('cpu_percent', sortedby))
            # MEM%
            self.term_window.addnstr(
                monitor_y + 2, process_x + 18,
                format(_("MEM%"), '>5'), 5,
                self.getProcessColumnColor('memory_percent', sortedby))
            process_name_x = 24
            # If screen space (X) is available then:
            # PID
            if tag_pid:
                self.term_window.addnstr(
                    monitor_y + 2, process_x + process_name_x,
                    format(_("PID"), '>5'), 5)
                process_name_x += 6
            # UID
            if tag_uid:
                self.term_window.addnstr(
                    monitor_y + 2, process_x + process_name_x,
                    _("USER"), 4)
                process_name_x += 11
            # NICE
            if tag_nice:
                self.term_window.addnstr(
                    monitor_y + 2, process_x + process_name_x,
                    format(_("NI"), '>3'), 3)
                process_name_x += 4
            # STATUS
            if tag_status:
                self.term_window.addnstr(
                    monitor_y + 2, process_x + process_name_x,
                    _("S"), 1)
                process_name_x += 2
            # TIME+
            if tag_proc_time:
                self.term_window.addnstr(
                    monitor_y + 2, process_x + process_name_x,
                    format(_("TIME+"), '>8'), 8)
                process_name_x += 9
            # IO
            if tag_io:
                self.term_window.addnstr(
                    monitor_y + 2, process_x + process_name_x,
                    format(_("IOR/s"), '>5'), 5,
                    self.getProcessColumnColor('io_counters', sortedby))
                process_name_x += 6
                self.term_window.addnstr(
                    monitor_y + 2, process_x + process_name_x,
                    format(_("IOW/s"), '>5'), 5,
                    self.getProcessColumnColor('io_counters', sortedby))
                process_name_x += 6
            # TCP/UDP
            # if tag_tcpudp:
            #     self.term_window.addnstr(
            #         monitor_y + 2, process_x + process_name_x,
            #         format(_("TCP"), '>5'), 5,
            #         self.getProcessColumnColor('tcp', sortedby))
            #     process_name_x += 6
            #     self.term_window.addnstr(
            #         monitor_y + 2, process_x + process_name_x,
            #         format(_("UDP"), '>5'), 5,
            #         self.getProcessColumnColor('udp', sortedby))
            #     process_name_x += 6
            # PROCESS NAME
            self.term_window.addnstr(
                monitor_y + 2, process_x + process_name_x,
                _("NAME"), 12, curses.A_UNDERLINE
                if sortedby == 'name' else 0)

            # If there is no data to display...
            if not processlist:
                self.term_window.addnstr(monitor_y + 3, self.process_x,
                                         _("Compute data..."), 15)
                return 6

            # Display the processes list
            # How many processes are going to be displayed ?
            proc_num = min(screen_y - monitor_y - log_count - 5,
                           len(processlist))

            # Loop to display processes
            for processes in range(0, proc_num):
                # VMS
                process_size = processlist[processes]['memory_info'][1]
                self.term_window.addnstr(
                    monitor_y + 3 + processes, process_x,
                    format(self.__autoUnit(process_size, low_precision=True),
                           '>5'), 5)
                # RSS
                process_resident = processlist[processes]['memory_info'][0]
                self.term_window.addnstr(
                    monitor_y + 3 + processes, process_x + 6,
                    format(self.__autoUnit(process_resident, low_precision=True),
                           '>5'), 5)
                # CPU%
                cpu_percent = processlist[processes]['cpu_percent']
                self.term_window.addnstr(
                    monitor_y + 3 + processes, process_x + 12,
                    format(cpu_percent, '>5.1f'), 5,
                    self.__getProcessCpuColor2(cpu_percent, core=core))
                # MEM%
                memory_percent = processlist[processes]['memory_percent']
                self.term_window.addnstr(
                    monitor_y + 3 + processes, process_x + 18,
                    format(memory_percent, '>5.1f'), 5,
                    self.__getProcessMemColor2(memory_percent))
                # If screen space (X) is available then:
                # PID
                if tag_pid:
                    pid = processlist[processes]['pid']
                    self.term_window.addnstr(
                        monitor_y + 3 + processes, process_x + 24,
                        format(str(pid), '>5'), 5)
                # UID
                if tag_uid:
                    uid = processlist[processes]['username']
                    self.term_window.addnstr(
                        monitor_y + 3 + processes, process_x + 30,
                        str(uid), 9)
                # NICE
                if tag_nice:
                    nice = processlist[processes]['nice']
                    self.term_window.addnstr(
                        monitor_y + 3 + processes, process_x + 41,
                        format(str(nice), '>3'), 3)
                # STATUS
                if tag_status:
                    status = processlist[processes]['status']
                    self.term_window.addnstr(
                        monitor_y + 3 + processes, process_x + 45,
                        str(status), 1)
                # TIME+
                if tag_proc_time:
                    process_time = processlist[processes]['cpu_times']
                    try:
                        dtime = timedelta(seconds=sum(process_time))
                    except Exception:
                        # Catched on some Amazon EC2 server
                        # See https://github.com/nicolargo/glances/issues/87
                        tag_proc_time = False
                    else:
                        dtime = "{0}:{1}.{2}".format(
                            str(dtime.seconds // 60 % 60),
                            str(dtime.seconds % 60).zfill(2),
                            str(dtime.microseconds)[:2].zfill(2))
                        self.term_window.addnstr(
                            monitor_y + 3 + processes, process_x + 47,
                            format(dtime, '>8'), 8)
                # IO
                # Hack to allow client 1.6 to connect to server 1.5.2
                process_tag_io = True
                try:
                    if processlist[processes]['io_counters'][4] == 0:
                        process_tag_io = True
                except Exception:
                    process_tag_io = False
                if tag_io:
                    if not process_tag_io:
                        # If io_tag == 0 (['io_counters'][4])
                        # then do not diplay IO rate
                        self.term_window.addnstr(
                            monitor_y + 3 + processes, process_x + 56,
                            format("?", '>5'), 5)
                        self.term_window.addnstr(
                            monitor_y + 3 + processes, process_x + 62,
                            format("?", '>5'), 5)
                    else:
                        # If io_tag == 1 (['io_counters'][4])
                        # then diplay IO rate
                        io_read = processlist[processes]['io_counters'][0]
                        io_read_old = processlist[processes]['io_counters'][2]
                        io_write = processlist[processes]['io_counters'][1]
                        io_write_old = processlist[processes]['io_counters'][3]
                        elapsed_time = max(1, self.__refresh_time)
                        io_rs = (io_read - io_read_old) / elapsed_time
                        io_ws = (io_write - io_write_old) / elapsed_time
                        self.term_window.addnstr(
                            monitor_y + 3 + processes, process_x + 56,
                            format(self.__autoUnit(io_rs, low_precision=True),
                                   '>5'), 5)
                        self.term_window.addnstr(
                            monitor_y + 3 + processes, process_x + 62,
                            format(self.__autoUnit(io_ws, low_precision=True),
                                   '>5'), 5)
                # TCP/UDP connexion number
                # if tag_tcpudp:
                #     try:
                #         processlist[processes]['tcp']
                #         processlist[processes]['udp']
                #     except:
                #         pass
                #     else:
                #         self.term_window.addnstr(
                #             monitor_y + 3 + processes, process_x + 68,
                #             format(processlist[processes]['tcp'], '>5'), 5)
                #         self.term_window.addnstr(
                #             monitor_y + 3 + processes, process_x + 74,
                #             format(processlist[processes]['udp'], '>5'), 5)
                # Display process command line
                max_process_name = screen_x - process_x - process_name_x
                process_name = processlist[processes]['name']
                process_cmdline = processlist[processes]['cmdline']
                if (len(process_cmdline) > max_process_name or
                    len(process_cmdline) == 0):
                    command = process_name
                else:
                    command = process_cmdline
                try:
                    self.term_window.addnstr(monitor_y + 3 + processes,
                                             process_x + process_name_x,
                                             command, max_process_name)
                except UnicodeEncodeError:
                    self.term_window.addnstr(monitor_y + 3 + processes,
                                             process_x + process_name_x,
                                             process_name, max_process_name)                    