    def _comparison(self, other, compare):
        """Compare self with other using operator.eq or operator.ne.

        When either of the elements is masked, the result is masked as well,
        but the underlying boolean data are still set, with self and other
        considered equal if both are masked, and unequal otherwise.

        For structured arrays, all fields are combined, with masked values
        ignored. The result is masked if all fields were masked, with self
        and other considered equal only if both were fully masked.
        """
        omask = getmask(other)
        smask = self.mask
        mask = mask_or(smask, omask, copy=True)

        odata = getdata(other)
        if mask.dtype.names:
            # For possibly masked structured arrays we need to be careful,
            # since the standard structured array comparison will use all
            # fields, masked or not. To avoid masked fields influencing the
            # outcome, we set all masked fields in self to other, so they'll
            # count as equal.  To prepare, we ensure we have the right shape.
            broadcast_shape = np.broadcast(self, odata).shape
            sbroadcast = np.broadcast_to(self, broadcast_shape, subok=True)
            sbroadcast._mask = mask
            sdata = sbroadcast.filled(odata)
            # Now take care of the mask; the merged mask should have an item
            # masked if all fields were masked (in one and/or other).
            mask = (mask == np.ones((), mask.dtype))

        else:
            # For regular arrays, just use the data as they come.
            sdata = self.data

        check = compare(sdata, odata)

        if isinstance(check, (np.bool_, bool)):
            return masked if mask else check

        if mask is not nomask:
            # Adjust elements that were masked, which should be treated
            # as equal if masked in both, unequal if masked in one.
            # Note that this works automatically for structured arrays too.
            check = np.where(mask, compare(smask, omask), check)
            if mask.shape != check.shape:
                # Guarantee consistency of the shape, making a copy since the
                # the mask may need to get written to later.
                mask = np.broadcast_to(mask, check.shape).copy()

        check = check.view(type(self))
        check._update_from(self)
        check._mask = mask

        # Cast fill value to bool_ if needed. If it cannot be cast, the
        # default boolean fill value is used.
        if check._fill_value is not None:
            try:
                fill = _check_fill_value(check._fill_value, np.bool_)
            except (TypeError, ValueError):
                fill = _check_fill_value(None, np.bool_)
            check._fill_value = fill

        return check