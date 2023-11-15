    def update(self, n=1):
        """
        Manually update the progress bar, useful for streams
        such as reading files.
        E.g.:
        >>> t = tqdm(total=filesize) # Initialise
        >>> for current_buffer in stream:
        ...    ...
        ...    t.update(len(current_buffer))
        >>> t.close()
        The last line is highly recommended, but possibly not necessary if
        `t.update()` will be called in such a way that `filesize` will be
        exactly reached and printed.
        Parameters
        ----------
        n  : int, optional
            Increment to add to the internal counter of iterations
            [default: 1].
        """
        # N.B.: see __iter__() for more comments.
        if self.disable:
            return

        if n < 0:
            raise ValueError("n ({0}) cannot be negative".format(n))
        self.n += n

        # check counter first to reduce calls to time()
        if self.n - self.last_print_n >= self.miniters:
            delta_t = self._time() - self.last_print_t
            if delta_t >= self.mininterval:
                cur_t = self._time()
                delta_it = self.n - self.last_print_n  # >= n
                # elapsed = cur_t - self.start_t
                # EMA (not just overall average)
                if self.smoothing and delta_t and delta_it:
                    self.avg_time = delta_t / delta_it \
                        if self.avg_time is None \
                        else self.smoothing * delta_t / delta_it + \
                        (1 - self.smoothing) * self.avg_time

                if not hasattr(self, "sp"):
                    raise TqdmDeprecationWarning("""\
Please use `tqdm_gui(...)` instead of `tqdm(..., gui=True)`
""", fp_write=getattr(self.fp, 'write', sys.stderr.write))

                with self._lock:
                    if self.pos:
                        self.moveto(abs(self.pos))

                    # Print bar update
                    self.sp(self.__repr__())

                    if self.pos:
                        self.moveto(-abs(self.pos))

                # If no `miniters` was specified, adjust automatically to the
                # maximum iteration rate seen so far between two prints.
                # e.g.: After running `tqdm.update(5)`, subsequent
                # calls to `tqdm.update()` will only cause an update after
                # at least 5 more iterations.
                if self.dynamic_miniters:
                    if self.maxinterval and delta_t >= self.maxinterval:
                        if self.mininterval:
                            self.miniters = delta_it * self.mininterval \
                                / delta_t
                        else:
                            self.miniters = delta_it * self.maxinterval \
                                / delta_t
                    elif self.smoothing:
                        self.miniters = self.smoothing * delta_it * \
                            (self.mininterval / delta_t
                             if self.mininterval and delta_t
                             else 1) + \
                            (1 - self.smoothing) * self.miniters
                    else:
                        self.miniters = max(self.miniters, delta_it)

                # Store old values for next call
                self.last_print_n = self.n
                self.last_print_t = cur_t