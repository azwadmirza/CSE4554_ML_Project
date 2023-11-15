    def _writer_daemon(self, stdin):
        """Daemon that writes output to the log file and stdout."""
        # Use line buffering (3rd param = 1) since Python 3 has a bug
        # that prevents unbuffered text I/O.
        in_pipe = os.fdopen(self.read_fd, 'r', 1)
        os.close(self.write_fd)

        echo = self.echo        # initial echo setting, user-controllable
        force_echo = False      # parent can force echo for certain output

        # list of streams to select from
        istreams = [in_pipe, stdin] if stdin else [in_pipe]

        log_file = self.log_file

        def handle_write(force_echo):
            # Handle output from the with block process.
            # If we arrive here it means that in_pipe was
            # ready for reading : it should never happen that
            # line is false-ish
            line = in_pipe.readline()
            if not line:
                return (True, force_echo)  # break while loop

            # find control characters and strip them.
            controls = control.findall(line)
            line = re.sub(control, '', line)

            # Echo to stdout if requested or forced
            if echo or force_echo:
                try:
                    if termios:
                        conf = termios.tcgetattr(sys.stdout)
                        tostop = conf[3] & termios.TOSTOP
                    else:
                        tostop = True
                except Exception:
                    tostop = True
                if not (tostop and _is_background_tty()):
                    sys.stdout.write(line)
                    sys.stdout.flush()

            # Stripped output to log file.
            log_file.write(_strip(line))
            log_file.flush()

            if xon in controls:
                force_echo = True
            if xoff in controls:
                force_echo = False
            return (False, force_echo)

        try:
            with _keyboard_input(stdin):
                while True:
                    # No need to set any timeout for select.select
                    # Wait until a key press or an event on in_pipe.
                    rlist, _, _ = select.select(istreams, [], [])
                    # Allow user to toggle echo with 'v' key.
                    # Currently ignores other chars.
                    # only read stdin if we're in the foreground
                    if stdin in rlist and not _is_background_tty():
                        if stdin.read(1) == 'v':
                            echo = not echo

                    if in_pipe in rlist:
                        br, fe = handle_write(force_echo)
                        force_echo = fe
                        if br:
                            break

        except BaseException:
            tty.error("Exception occurred in writer daemon!")
            traceback.print_exc()

        finally:
            # send written data back to parent if we used a StringIO
            if self.write_log_in_parent:
                self.child.send(log_file.getvalue())
            log_file.close()

        # send echo value back to the parent so it can be preserved.
        self.child.send(echo)