    def displayProcess(self, processcount, processlist, log_count=0):
        # Process
        if not processcount:
            return 0
        screen_x = self.screen.getmaxyx()[1]
        screen_y = self.screen.getmaxyx()[0]
        # If there is no network & diskio & fs stats
        # then increase process window
        if (not self.network_tag and
            not self.diskio_tag and
            not self.fs_tag):
            process_x = 0
        else:
            process_x = self.process_x
        # Display the process summary
        if (screen_y > self.process_y + 4 and
            screen_x > process_x + 48):
            # Processes sumary
            self.term_window.addnstr(self.process_y, process_x, _("Processes"),
                                     9, self.title_color if self.hascolors else
                                     curses.A_UNDERLINE)
            other = (processcount['total'] -
                     stats.getProcessCount()['running'] -
                     stats.getProcessCount()['sleeping'])
            self.term_window.addnstr(
                self.process_y, process_x + 10,
                "{0}, {1} {2}, {3} {4}, {5} {6}".format(
                    str(processcount['total']),
                    str(processcount['running']),
                    _("running"),
                    str(processcount['sleeping']),
                    _("sleeping"),
                    str(other),
                    _("other")), 42)

        # Processes detail
        if (screen_y > self.process_y + 4 and
            screen_x > process_x + 49):

            # Display the process detail
            tag_pid = False
            tag_uid = False
            tag_nice = False
            tag_status = False
            tag_proc_time = False
            tag_io = False
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
            if screen_x > process_x + 97:
                tag_io = True

            if not psutil_get_io_counter_tag:
                tag_io = False
                
            # VMS
            self.term_window.addnstr(
                self.process_y + 2, process_x,
                _("VIRT"), 5)
            # RSS
            self.term_window.addnstr(
                self.process_y + 2, process_x + 7,
                _("RES"), 5)
            # CPU%
            self.term_window.addnstr(
                self.process_y + 2, process_x + 14,
                _("CPU%"), 5, curses.A_UNDERLINE
                if self.getProcessSortedBy() == 'cpu_percent' else 0)
            # MEM%
            self.term_window.addnstr(
                self.process_y + 2, process_x + 21,
                _("MEM%"), 5, curses.A_UNDERLINE
                if self.getProcessSortedBy() == 'memory_percent' else 0)
            process_name_x = 28
            # If screen space (X) is available then:
            # PID
            if tag_pid:
                self.term_window.addnstr(
                    self.process_y + 2, process_x + process_name_x,
                    _("PID"), 6)
                process_name_x += 7
            # UID
            if tag_uid:
                self.term_window.addnstr(
                    self.process_y + 2, process_x + process_name_x,
                    _("USER"), 8)
                process_name_x += 10
            # NICE
            if tag_nice:
                self.term_window.addnstr(
                    self.process_y + 2, process_x + process_name_x,
                    _("NI"), 3)
                process_name_x += 4
            # STATUS
            if tag_status:
                self.term_window.addnstr(
                    self.process_y + 2, process_x + process_name_x,
                    _("S"), 1)
                process_name_x += 3
            # TIME+
            if tag_proc_time:
                self.term_window.addnstr(
                    self.process_y + 2, process_x + process_name_x,
                    _("TIME+"), 8)
                process_name_x += 10
            # IO
            if tag_io:
                self.term_window.addnstr(
                    self.process_y + 2, process_x + process_name_x,
                    _("IO_R"), 6)
                process_name_x += 8
                self.term_window.addnstr(
                    self.process_y + 2, process_x + process_name_x,
                    _("IO_W"), 6)
                process_name_x += 8               
            # PROCESS NAME
            self.term_window.addnstr(
                self.process_y + 2, process_x + process_name_x,
                _("NAME"), 12, curses.A_UNDERLINE
                if self.getProcessSortedBy() == 'name' else 0)

            # If there is no data to display...
            if not processlist:
                self.term_window.addnstr(self.process_y + 3, self.process_x,
                                         _("Compute data..."), 15)
                return 6

            proc_num = min(screen_y - self.term_h +
                           self.process_y - log_count + 5,
                           len(processlist))
            for processes in range(0, proc_num):
                # VMS
                process_size = processlist[processes]['memory_info'][1]
                self.term_window.addnstr(
                    self.process_y + 3 + processes, process_x,
                    self.__autoUnit(process_size), 5)
                # RSS
                process_resident = processlist[processes]['memory_info'][0]
                self.term_window.addnstr(
                    self.process_y + 3 + processes, process_x + 7,
                    self.__autoUnit(process_resident), 5)
                # CPU%
                cpu_percent = processlist[processes]['cpu_percent']
                if psutil_get_cpu_percent_tag:
                    self.term_window.addnstr(
                        self.process_y + 3 + processes, process_x + 14,
                        "{0:.1f}".format(cpu_percent), 5,
                        self.__getProcessColor(cpu_percent))
                else:
                    self.term_window.addnstr(
                        self.process_y + 3 + processes, process_x, "N/A", 8)
                # MEM%
                memory_percent = processlist[processes]['memory_percent']
                self.term_window.addnstr(
                    self.process_y + 3 + processes, process_x + 21,
                    "{0:.1f}".format(memory_percent), 5,
                    self.__getProcessColor(memory_percent))
                # If screen space (X) is available then:
                # PID
                if tag_pid:
                    pid = processlist[processes]['pid']
                    self.term_window.addnstr(
                        self.process_y + 3 + processes, process_x + 28,
                        str(pid), 6)
                # UID
                if tag_uid:
                    uid = processlist[processes]['username']
                    self.term_window.addnstr(
                        self.process_y + 3 + processes, process_x + 35,
                        str(uid), 8)
                # NICE
                if tag_nice:
                    nice = processlist[processes]['nice']
                    self.term_window.addnstr(
                        self.process_y + 3 + processes, process_x + 45,
                        str(nice), 3)
                # STATUS
                if tag_status:
                    status = processlist[processes]['status']
                    self.term_window.addnstr(
                        self.process_y + 3 + processes, process_x + 49,
                        str(status), 1)
                # TIME+
                if tag_proc_time:
                    process_time = processlist[processes]['cpu_times']
                    try:                        
                        dtime = timedelta(seconds=sum(process_time))
                    except:
                        # Catched on some Amazon EC2 server
                        # See https://github.com/nicolargo/glances/issues/87
                        tag_proc_time = False
                    else:
                        dtime = "{0}:{1}.{2}".format(
                                    str(dtime.seconds // 60 % 60).zfill(2),
                                    str(dtime.seconds % 60).zfill(2),
                                    str(dtime.microseconds)[:2])
                        self.term_window.addnstr(
                            self.process_y + 3 + processes, process_x + 52,
                            dtime, 8)
                # IO
                if tag_io:
                    if processlist[processes]['io_counters'] == {}:
                        self.term_window.addnstr(
                            self.process_y + 3 + processes, process_x + 62,
                            _("A_DENY"), 6)
                        self.term_window.addnstr(
                            self.process_y + 3 + processes, process_x + 70,
                            _("A_DENY"), 6)
                    else:
                        # Processes are only refresh every 2 refresh_time
                        #~ elapsed_time = max(1, self.__refresh_time) * 2
                        io_read = processlist[processes]['io_counters'][2]
                        self.term_window.addnstr(
                            self.process_y + 3 + processes, process_x + 62,
                            self.__autoUnit(io_read), 6)
                        io_write = processlist[processes]['io_counters'][3]
                        self.term_window.addnstr(
                            self.process_y + 3 + processes, process_x + 70,
                            self.__autoUnit(io_write), 6)
                        
                # display process command line
                max_process_name = screen_x - process_x - process_name_x
                process_name = processlist[processes]['name']
                process_cmdline = processlist[processes]['cmdline']
                if (len(process_cmdline) > max_process_name or
                    len(process_cmdline) == 0):
                    command = process_name
                else:
                    command = process_cmdline
                self.term_window.addnstr(self.process_y + 3 + processes,
                                         process_x + process_name_x,
                                         command, max_process_name)