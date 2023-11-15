    def __iter__(self):
        ''' Backward-compatibility to use: for x in tqdm(iterable) '''

        # Inlining instance variables as locals (speed optimisation)
        iterable = self.iterable

        # If the bar is disabled, then just walk the iterable
        # (note: keep this check outside the loop for performance)
        if self.disable:
            for obj in iterable:
                yield obj
        else:
            ncols = self.ncols
            mininterval = self.mininterval
            maxinterval = self.maxinterval
            miniters = self.miniters
            dynamic_miniters = self.dynamic_miniters
            unit = self.unit
            unit_scale = self.unit_scale
            ascii = self.ascii
            start_t = self.start_t
            last_print_t = self.last_print_t
            last_print_n = self.last_print_n
            n = self.n
            dynamic_ncols = self.dynamic_ncols
            smoothing = self.smoothing
            avg_time = self.avg_time
            bar_format = self.bar_format
            _time = self._time
            format_meter = self.format_meter

            try:
                sp = self.sp
            except AttributeError:
                raise TqdmDeprecationWarning("""\
Please use `tqdm_gui(...)` instead of `tqdm(..., gui=True)`
""", fp_write=getattr(self.fp, 'write', sys.stderr.write))

            for obj in iterable:
                yield obj
                # Update and print the progressbar.
                # Note: does not call self.update(1) for speed optimisation.
                n += 1
                # check the counter first (avoid calls to time())
                if n - last_print_n >= miniters:
                    delta_t = _time() - last_print_t
                    if delta_t >= mininterval:
                        cur_t = _time()
                        delta_it = n - last_print_n
                        elapsed = cur_t - start_t
                        # EMA (not just overall average)
                        if smoothing and delta_t and delta_it:
                            avg_time = delta_t / delta_it \
                                if avg_time is None \
                                else smoothing * delta_t / delta_it + \
                                (1 - smoothing) * avg_time

                        if self.pos:
                            self.moveto(self.pos)

                        # Printing the bar's update
                        sp(format_meter(
                            n, self.total, elapsed,
                            (dynamic_ncols(self.fp) if dynamic_ncols
                             else ncols),
                            self.desc, ascii, unit, unit_scale,
                            1 / avg_time if avg_time else None, bar_format))

                        if self.pos:
                            self.moveto(-self.pos)

                        # If no `miniters` was specified, adjust automatically
                        # to the maximum iteration rate seen so far.
                        if dynamic_miniters:
                            if maxinterval and delta_t > maxinterval:
                                # Set miniters to correspond to maxinterval
                                miniters = delta_it * maxinterval / delta_t
                            elif mininterval and delta_t:
                                # EMA-weight miniters to converge
                                # towards the timeframe of mininterval
                                miniters = smoothing * delta_it * mininterval \
                                    / delta_t + (1 - smoothing) * miniters
                            else:
                                miniters = smoothing * delta_it + \
                                           (1 - smoothing) * miniters

                        # Store old values for next call
                        self.n = self.last_print_n = last_print_n = n
                        self.last_print_t = last_print_t = cur_t

            # Closing the progress bar.
            # Update some internal variables for close().
            self.last_print_n = last_print_n
            self.n = n
            self.close()