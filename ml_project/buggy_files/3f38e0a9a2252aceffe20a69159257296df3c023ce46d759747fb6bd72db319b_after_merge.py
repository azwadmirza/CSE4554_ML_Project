    def check_slice_indices(self, start, stop, step):
        """Check frame indices are valid and clip to fit trajectory.

        The usage follows standard Python conventions for :func:`range` but see
        the warning below.

        Parameters
        ----------
        start : int or None
          Starting frame index (inclusive). ``None`` corresponds to the default
          of 0, i.e., the initial frame.
        stop : int or None
          Last frame index (exclusive). ``None`` corresponds to the default
          of n_frames, i.e., it includes the last frame of the trajectory.
        step : int or None
          step size of the slice, ``None`` corresponds to the default of 1, i.e,
          include every frame in the range `start`, `stop`.

        Returns
        -------
        start, stop, step : tuple (int, int, int)
          Integers representing the slice

        Warning
        -------
        The returned values `start`, `stop` and `step` give the expected result
        when passed in :func:`range` but gives unexpected behavior when passed
        in a :class:`slice` when ``stop=None`` and ``step=-1``

        This can be a problem for downstream processing of the output from this
        method. For example, slicing of trajectories is implemented by passing
        the values returned by :meth:`check_slice_indices` to :func:`range` ::

          range(start, stop, step)

        and using them as the indices to randomly seek to. On the other hand,
        in :class:`MDAnalysis.analysis.base.AnalysisBase` the values returned
        by :meth:`check_slice_indices` are used to splice the trajectory by
        creating a :class:`slice` instance ::

          slice(start, stop, step)

        This creates a discrepancy because these two lines are not equivalent::

            range(10, -1, -1)             # [10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
            range(10)[slice(10, -1, -1)]  # []

        """

        slice_dict = {'start': start, 'stop': stop, 'step': step}
        for varname, var in slice_dict.items():
            if isinstance(var, numbers.Integral):
                slice_dict[varname] = int(var)
            elif (var is None):
                pass
            else:
                raise TypeError("{0} is not an integer".format(varname))

        start = slice_dict['start']
        stop = slice_dict['stop']
        step = slice_dict['step']

        if step == 0:
            raise ValueError("Step size is zero")

        nframes = len(self)
        step = step or 1

        if start is None:
            start = 0 if step > 0 else nframes - 1
        elif start < 0:
            start += nframes
        if start < 0:
            start = 0

        if step < 0 and start >= nframes:
            start = nframes - 1

        if stop is None:
            stop = nframes if step > 0 else -1
        elif stop < 0:
            stop += nframes

        if step > 0 and stop > nframes:
            stop = nframes

        return start, stop, step