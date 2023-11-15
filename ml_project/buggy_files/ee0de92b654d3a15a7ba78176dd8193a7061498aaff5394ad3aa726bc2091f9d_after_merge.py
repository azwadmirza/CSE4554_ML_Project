    def _balance(self):
        """
        Balance the table. This means to make sure
        all cells on the same row have the same height,
        that all columns have the same number of rows
        and that the table fits within the given width.
        """

        # we make all modifications on a working copy of the
        # actual table. This allows us to add columns/rows
        # and re-balance over and over without issue.
        self.worktable = deepcopy(self.table)

        self._borders()
        return
        options = copy(self.options)

        # balance number of rows to make a rectangular table
        # column by column
        ncols = len(self.worktable)
        nrows = [len(col) for col in self.worktable]
        nrowmax = max(nrows) if nrows else 0
        for icol, nrow in enumerate(nrows):
            self.worktable[icol].reformat(**options)
            if nrow < nrowmax:
                # add more rows to too-short columns
                empty_rows = ["" for _ in range(nrowmax-nrow)]
                self.worktable[icol].add_rows(*empty_rows)
        self.ncols = ncols
        self.nrows = nrowmax

        # add borders - these add to the width/height, so we must do this before calculating width/height
        self._borders()

        # equalize widths within each column
        cwidths = [max(cell.get_width() for cell in col) for col in self.worktable]

        if self.width or self.maxwidth and self.maxwidth < sum(cwidths):
            # we set a table width. Horizontal cells will be evenly distributed and
            # expand vertically as needed (unless self.height is set, see below)

            # use fixed width, or set to maxwidth
            width = self.width if self.width else self.maxwidth

            if ncols:
                # get minimum possible cell widths for each row
                cwidths_min = [max(cell.get_min_width() for cell in col) for col in self.worktable]
                cwmin = sum(cwidths_min)

                if cwmin > width:
                    # we cannot shrink any more
                    raise Exception("Cannot shrink table width to %s. Minimum size is %s." % (self.width, cwmin))

                excess = width - cwmin
                if self.evenwidth:
                    # make each column of equal width
                    for _ in range(excess):
                        # flood-fill the minimum table starting with the smallest columns
                        ci = cwidths_min.index(min(cwidths_min))
                        cwidths_min[ci] += 1
                    cwidths = cwidths_min
                else:
                    # make each column expand more proportional to their data size
                    for _ in range(excess):
                        # fill wider columns first
                        ci = cwidths.index(max(cwidths))
                        cwidths_min[ci] += 1
                        cwidths[ci] -= 3
                    cwidths = cwidths_min

        # reformat worktable (for width align)
        for ix, col in enumerate(self.worktable):
            try:
                col.reformat(width=cwidths[ix], **options)
            except Exception:
                raise

        # equalize heights for each row (we must do this here, since it may have changed to fit new widths)
        cheights = [max(cell.get_height() for cell in (col[iy] for col in self.worktable)) for iy in range(nrowmax)]

        if self.height:
            # if we are fixing the table height, it means cells must crop text instead of resizing.
            if nrowmax:

                # get minimum possible cell heights for each column
                cheights_min = [max(cell.get_min_height()
                                    for cell in (col[iy] for col in self.worktable)) for iy in range(nrowmax)]
                chmin = sum(cheights_min)

                if chmin > self.height:
                    # we cannot shrink any more
                    raise Exception("Cannot shrink table height to %s. Minimum size is %s." % (self.height, chmin))

                # now we add all the extra height up to the desired table-height.
                # We do this so that the tallest cells gets expanded first (and
                # thus avoid getting cropped)

                excess = self.height - chmin
                even = self.height % 2 == 0
                for position in range(excess):
                    # expand the cells with the most rows first
                    if 0 <= position < nrowmax and nrowmax > 1:
                        # avoid adding to header first round (looks bad on very small tables)
                        ci = cheights[1:].index(max(cheights[1:])) + 1
                    else:
                        ci = cheights.index(max(cheights))
                    cheights_min[ci] += 1
                    if ci == 0 and self.header:
                        # it doesn't look very good if header expands too fast
                        cheights[ci] -= 2 if even else 3
                    cheights[ci] -= 2 if even else 1
                cheights = cheights_min

                # we must tell cells to crop instead of expanding
            options["enforce_size"] = True

        # reformat table (for vertical align)
        for ix, col in enumerate(self.worktable):
            for iy, cell in enumerate(col):
                try:
                    col.reformat_cell(iy, height=cheights[iy], **options)
                except Exception as e:
                    msg = "ix=%s, iy=%s, height=%s: %s" % (ix, iy, cheights[iy], e.message)
                    raise Exception("Error in vertical align:\n %s" % msg)

        # calculate actual table width/height in characters
        self.cwidth = sum(cwidths)
        self.cheight = sum(cheights)