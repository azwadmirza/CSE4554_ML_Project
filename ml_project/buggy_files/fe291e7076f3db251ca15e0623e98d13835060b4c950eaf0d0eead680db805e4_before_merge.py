    def eventplot(self, positions, orientation='horizontal', lineoffsets=1,
                  linelengths=1, linewidths=None, colors=None,
                  linestyles='solid', **kwargs):
        """
        Plot identical parallel lines at specific positions.

        Call signature::

          eventplot(positions, orientation='horizontal', lineoffsets=0,
                    linelengths=1, linewidths=None, color =None,
                    linestyles='solid'

        Plot parallel lines at the given positions.  positions should be a 1D
        or 2D array-like object, with each row corresponding to a row or column
        of lines.

        This type of plot is commonly used in neuroscience for representing
        neural events, where it is commonly called a spike raster, dot raster,
        or raster plot.

        However, it is useful in any situation where you wish to show the
        timing or position of multiple sets of discrete events, such as the
        arrival times of people to a business on each day of the month or the
        date of hurricanes each year of the last century.

        *orientation* : [ 'horizonal' | 'vertical' ]
          'horizonal' : the lines will be vertical and arranged in rows
          "vertical' : lines will be horizontal and arranged in columns

        *lineoffsets* :
          A float or array-like containing floats.

        *linelengths* :
          A float or array-like containing floats.

        *linewidths* :
          A float or array-like containing floats.

        *colors*
          must be a sequence of RGBA tuples (eg arbitrary color
          strings, etc, not allowed) or a list of such sequences

        *linestyles* :
          [ 'solid' | 'dashed' | 'dashdot' | 'dotted' ] or an array of these
          values

        For linelengths, linewidths, colors, and linestyles, if only a single
        value is given, that value is applied to all lines.  If an array-like
        is given, it must have the same length as positions, and each value
        will be applied to the corresponding row or column in positions.

        Returns a list of :class:`matplotlib.collections.EventCollection`
        objects that were added.

        kwargs are :class:`~matplotlib.collections.LineCollection` properties:

        %(LineCollection)s

        **Example:**

        .. plot:: mpl_examples/pylab_examples/eventplot_demo.py
        """
        self._process_unit_info(xdata=positions,
                                ydata=[lineoffsets, linelengths],
                                kwargs=kwargs)

        # We do the conversion first since not all unitized data is uniform
        positions = self.convert_xunits(positions)
        lineoffsets = self.convert_yunits(lineoffsets)
        linelengths = self.convert_yunits(linelengths)

        if not iterable(positions):
            positions = [positions]
        elif any(iterable(position) for position in positions):
            positions = [np.asanyarray(position) for position in positions]
        else:
            positions = [np.asanyarray(positions)]

        if len(positions) == 0:
            return []

        if not iterable(lineoffsets):
            lineoffsets = [lineoffsets]
        if not iterable(linelengths):
            linelengths = [linelengths]
        if not iterable(linewidths):
            linewidths = [linewidths]
        if not iterable(colors):
            colors = [colors]
        if hasattr(linestyles, 'lower') or not iterable(linestyles):
            linestyles = [linestyles]

        lineoffsets = np.asarray(lineoffsets)
        linelengths = np.asarray(linelengths)
        linewidths = np.asarray(linewidths)

        if len(lineoffsets) == 0:
            lineoffsets = [None]
        if len(linelengths) == 0:
            linelengths = [None]
        if len(linewidths) == 0:
            lineoffsets = [None]
        if len(linewidths) == 0:
            lineoffsets = [None]
        if len(colors) == 0:
            colors = [None]

        if len(lineoffsets) == 1 and len(positions) != 1:
            lineoffsets = np.tile(lineoffsets, len(positions))
            lineoffsets[0] = 0
            lineoffsets = np.cumsum(lineoffsets)
        if len(linelengths) == 1:
            linelengths = np.tile(linelengths, len(positions))
        if len(linewidths) == 1:
            linewidths = np.tile(linewidths, len(positions))
        if len(colors) == 1:
            colors = np.asanyarray(colors)
            colors = np.tile(colors, [len(positions), 1])
        if len(linestyles) == 1:
            linestyles = [linestyles] * len(positions)

        if len(lineoffsets) != len(positions):
            raise ValueError('lineoffsets and positions are unequal sized '
                             'sequences')
        if len(linelengths) != len(positions):
            raise ValueError('linelengths and positions are unequal sized '
                             'sequences')
        if len(linewidths) != len(positions):
            raise ValueError('linewidths and positions are unequal sized '
                             'sequences')
        if len(colors) != len(positions):
            raise ValueError('colors and positions are unequal sized '
                             'sequences')
        if len(linestyles) != len(positions):
            raise ValueError('linestyles and positions are unequal sized '
                             'sequences')

        colls = []
        for position, lineoffset, linelength, linewidth, color, linestyle in \
            zip(positions, lineoffsets, linelengths, linewidths,
                           colors, linestyles):
            coll = mcoll.EventCollection(position,
                                         orientation=orientation,
                                         lineoffset=lineoffset,
                                         linelength=linelength,
                                         linewidth=linewidth,
                                         color=color,
                                         linestyle=linestyle)
            self.add_collection(coll, autolim=False)
            coll.update(kwargs)
            colls.append(coll)

        if len(positions) > 0:
            # try to get min/max
            min_max = [(np.min(_p), np.max(_p)) for _p in positions
                       if len(_p) > 0]
            # if we have any non-empty positions, try to autoscale
            if len(min_max) > 0:
                mins, maxes = zip(*min_max)
                minpos = np.min(mins)
                maxpos = np.max(maxes)

                minline = (lineoffsets - linelengths).min()
                maxline = (lineoffsets + linelengths).max()

                if colls[0].is_horizontal():
                    corners = (minpos, minline), (maxpos, maxline)
                else:
                    corners = (minline, minpos), (maxline, maxpos)
                self.update_datalim(corners)
                self.autoscale_view()

        return colls