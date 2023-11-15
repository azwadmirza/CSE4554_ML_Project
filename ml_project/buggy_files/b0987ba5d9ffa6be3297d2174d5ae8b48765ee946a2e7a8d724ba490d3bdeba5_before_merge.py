    def _searchsorted_monotonic(self, label, side, exclude_label=False):
        if not self.is_non_overlapping_monotonic:
            raise KeyError('can only get slices from an IntervalIndex if '
                           'bounds are non-overlapping and all monotonic '
                           'increasing or decreasing')

        if isinstance(label, IntervalMixin):
            raise NotImplementedError

        if ((side == 'left' and self.left.is_monotonic_increasing) or
                (side == 'right' and self.left.is_monotonic_decreasing)):
            sub_idx = self.right
            if self.open_right or exclude_label:
                label = _get_next_label(label)
        else:
            sub_idx = self.left
            if self.open_left or exclude_label:
                label = _get_prev_label(label)

        return sub_idx._searchsorted_monotonic(label, side)