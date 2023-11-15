    def _set_win_sizes(self):
        try:
            win_size = fcntl.ioctl(sys.stdout.fileno(),
                                   termios.TIOCGWINSZ, '\0' * 8)
        except OSError:  # eg. in MPI we can't do this
            rows, cols, xpix, ypix = 25, 80, 0, 0
        else:
            rows, cols, xpix, ypix = struct.unpack('HHHH', win_size)

        if cols == 0:
            cols = 80

        win_size = struct.pack("HHHH", rows, cols, xpix, ypix)

        for fd in self.fds:
            try:
                fcntl.ioctl(fd, termios.TIOCSWINSZ, win_size)
            except OSError:  # eg. in MPI we can't do this
                pass