    def _binary_operator_ruler(self, other, op_name):
        exception_message = (
            "Invalid dimensions for this operation")
        if isinstance(other, Signal):
            # Both objects are signals
            oam = other.axes_manager
            sam = self.axes_manager
            if sam.navigation_shape == oam.navigation_shape and \
                    sam.signal_shape == oam.signal_shape:
                # They have the same signal shape.
                # The signal axes are aligned but there is
                # no guarantee that data axes area aligned so we make sure that
                # they are aligned for the operation.
                sdata = self._data_aligned_with_axes
                odata = other._data_aligned_with_axes
                if op_name in INPLACE_OPERATORS:
                    self.data = getattr(sdata, op_name)(odata)
                    self.axes_manager._sort_axes()
                    return self
                else:
                    ns = self._deepcopy_with_new_data(
                        getattr(sdata, op_name)(odata))
                    ns.axes_manager._sort_axes()
                    return ns
            else:
                # Different navigation and/or signal shapes
                if not are_signals_aligned(self, other):
                    raise ValueError(exception_message)
                else:
                    # They are broadcastable but have different number of axes
                    new_nav_axes = []
                    for saxis, oaxis in zip(
                            sam.navigation_axes, oam.navigation_axes):
                        new_nav_axes.append(saxis if saxis.size > 1 or
                                            oaxis.size == 1 else
                                            oaxis)
                    if sam.navigation_dimension != oam.navigation_dimension:
                        bigger_am = (sam
                                     if sam.navigation_dimension >
                                     oam.navigation_dimension
                                     else oam)
                        new_nav_axes.extend(
                            bigger_am.navigation_axes[len(new_nav_axes):])
                    # Because they are broadcastable and navigation axes come
                    # first in the data array, we don't need to pad the data
                    # array.
                    new_sig_axes = []
                    for saxis, oaxis in zip(
                            sam.signal_axes, oam.signal_axes):
                        new_sig_axes.append(saxis if saxis.size > 1 or
                                            oaxis.size == 1 else
                                            oaxis)
                    if sam.signal_dimension != oam.signal_dimension:
                        bigger_am = (
                            sam if sam.signal_dimension > oam.signal_dimension
                            else oam)
                        new_sig_axes.extend(
                            bigger_am.signal_axes[len(new_sig_axes):])
                    sdim_diff = abs(sam.signal_dimension -
                                    oam.signal_dimension)
                    sdata = self._data_aligned_with_axes
                    odata = other._data_aligned_with_axes
                    if len(new_nav_axes) and sdim_diff:
                        if bigger_am is sam:
                            # Pad odata
                            while sdim_diff:
                                odata = np.expand_dims(
                                    odata, oam.navigation_dimension)
                                sdim_diff -= 1
                        else:
                            # Pad sdata
                            while sdim_diff:
                                sdata = np.expand_dims(
                                    sdata, sam.navigation_dimension)
                                sdim_diff -= 1
                    if op_name in INPLACE_OPERATORS:
                        # This should raise a ValueError if the operation
                        # changes the shape of the object on the left.
                        self.data = getattr(sdata, op_name)(odata)
                        self.axes_manager._sort_axes()
                        return self
                    else:
                        ns = self._deepcopy_with_new_data(
                            getattr(sdata, op_name)(odata))
                        new_axes = new_nav_axes[::-1] + new_sig_axes[::-1]
                        ns.axes_manager._axes = [axis.copy()
                                                 for axis in new_axes]
                        if bigger_am is oam:
                            ns.metadata.Signal.record_by = \
                                other.metadata.Signal.record_by
                            ns._assign_subclass()
                        return ns

        else:
            # Second object is not a Signal
            if op_name in INPLACE_OPERATORS:
                getattr(self.data, op_name)(other)
                return self
            else:
                return self._deepcopy_with_new_data(
                    getattr(self.data, op_name)(other))