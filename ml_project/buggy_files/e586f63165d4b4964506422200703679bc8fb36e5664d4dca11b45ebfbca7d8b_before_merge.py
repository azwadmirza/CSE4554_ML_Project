    def _slice_dataset(self, start, stop, step):
        """Return the element tags in the Dataset that match the slice.

        Parameters
        ----------
        start : int or 2-tuple of int or None
            The slice's starting element tag value, in any format accepted by
            pydicom.tag.Tag.
        stop : int or 2-tuple of int or None
            The slice's stopping element tag value, in any format accepted by
            pydicom.tag.Tag.
        step : int or None
            The slice's step size.

        Returns
        ------
        list of pydicom.tag.Tag
            The tags in the Dataset that meet the conditions of the slice.
        """
        # Check the starting/stopping Tags are valid when used
        if start is not None:
            start = Tag(start)
        if stop is not None:
            stop = Tag(stop)

        all_tags = sorted(self.tags.keys())
        # If the Dataset is empty, return an empty list
        if not all_tags:
            return []

        # Special case the common situations:
        #   - start and/or stop are None
        #   - step is 1

        if start is None:
            if stop is None:
                # For step=1 avoid copying the list
                return all_tags if step == 1 else all_tags[::step]
            else:  # Have a stop value, get values until that point
                step1_list = list(takewhile(lambda x: x < stop, all_tags))
                return step1_list if step == 1 else step1_list[::step]

        # Have a non-None start value.  Find its index
        i_start = bisect_left(all_tags, start)
        if stop is None:
            return all_tags[i_start::step]
        else:
            i_stop = bisect_left(all_tags, stop)
            return all_tags[i_start:i_stop:step]