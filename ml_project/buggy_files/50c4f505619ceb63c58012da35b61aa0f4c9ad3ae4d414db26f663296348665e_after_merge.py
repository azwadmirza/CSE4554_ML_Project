    def __init__(self, nbins=10, steps=None, trim=True, integer=False,
                 symmetric=False, prune=None):
            """
            Keyword args:
            *nbins*
                Maximum number of intervals; one less than max number of ticks.
            *steps*
                Sequence of nice numbers starting with 1 and ending with 10;
                e.g., [1, 2, 4, 5, 10]
            *integer*
                If True, ticks will take only integer values.
            *symmetric*
                If True, autoscaling will result in a range symmetric
                about zero.
            *prune*
                ['lower' | 'upper' | 'both' | None]
                Remove edge ticks -- useful for stacked or ganged plots
                where the upper tick of one axes overlaps with the lower
                tick of the axes above it.
                If prune=='lower', the smallest tick will
                be removed.  If prune=='upper', the largest tick will be
                removed.  If prune=='both', the largest and smallest ticks
                will be removed.  If prune==None, no ticks will be removed.
            """
            self._nbins = int(nbins)
            self._trim = trim
            self._integer = integer
            self._symmetric = symmetric
            if prune is not None and prune not in ['upper', 'lower', 'both']:
                raise ValueError(
                    "prune must be 'upper', 'lower', 'both', or None")
            self._prune = prune
            if steps is None:
                steps = [1, 2, 2.5, 3, 4, 5, 6, 8, 10]
            else:
                if int(steps[-1]) != 10:
                    steps = list(steps)
                    steps.append(10)
            self._steps = steps
            self._integer = integer
            if self._integer:
                self._steps = [n for n in self._steps
                               if divmod(n, 1)[1] < 0.001]