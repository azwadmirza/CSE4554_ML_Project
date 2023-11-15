    def unstack(self, level=-1):
        """
        "Unstack" level from MultiLevel index to produce reshaped DataFrame

        Parameters
        ----------
        level : int, string, or list of these, default last level
            Level(s) to unstack, can pass level name

        Examples
        --------
        >>> s
        one  a   1.
        one  b   2.
        two  a   3.
        two  b   4.

        >>> s.unstack(level=-1)
             a   b
        one  1.  2.
        two  3.  4.

        >>> s.unstack(level=0)
           one  two
        a  1.   2.
        b  3.   4.

        Returns
        -------
        unstacked : DataFrame
        """
        from pandas.core.reshape import unstack
        if isinstance(level, (tuple, list)):
            result = self
            for lev in level:
                result = unstack(result, lev)
            return result
        else:
            return unstack(self, level)