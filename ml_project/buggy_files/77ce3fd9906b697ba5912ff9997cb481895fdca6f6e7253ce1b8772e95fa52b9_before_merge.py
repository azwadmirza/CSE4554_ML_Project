    def replace(self, to_replace, value, inplace=False, filter=None,
                regex=False, convert=True, mgr=None):
        """ replace the to_replace value with value, possible to create new
        blocks here this is just a call to putmask. regex is not used here.
        It is used in ObjectBlocks.  It is here for API
        compatibility."""

        original_to_replace = to_replace

        # try to replace, if we raise an error, convert to ObjectBlock and retry
        try:
            values, _, to_replace, _ = self._try_coerce_args(self.values, to_replace)
            mask = com.mask_missing(values, to_replace)
            if filter is not None:
                filtered_out = ~self.mgr_locs.isin(filter)
                mask[filtered_out.nonzero()[0]] = False

            blocks = self.putmask(mask, value, inplace=inplace)
            if convert:
                blocks = [ b.convert(by_item=True, numeric=False, copy=not inplace) for b in blocks ]
            return blocks
        except (TypeError, ValueError):

            # we can't process the value, but nothing to do
            if not mask.any():
                return self if inplace else self.copy()

            return self.to_object_block(mgr=mgr).replace(to_replace=original_to_replace,
                                                         value=value,
                                                         inplace=inplace,
                                                         filter=filter,
                                                         regex=regex,
                                                         convert=convert)