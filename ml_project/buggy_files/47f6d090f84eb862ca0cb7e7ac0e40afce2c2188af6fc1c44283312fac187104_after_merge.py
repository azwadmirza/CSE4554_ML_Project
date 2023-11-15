    def write_array(self, key: str, obj: FrameOrSeries, items: Optional[Index] = None):
        # TODO: we only have a few tests that get here, the only EA
        #  that gets passed is DatetimeArray, and we never have
        #  both self._filters and EA

        value = extract_array(obj, extract_numpy=True)

        if key in self.group:
            self._handle.remove_node(self.group, key)

        # Transform needed to interface with pytables row/col notation
        empty_array = value.size == 0
        transposed = False

        if is_categorical_dtype(value.dtype):
            raise NotImplementedError(
                "Cannot store a category dtype in a HDF5 dataset that uses format="
                '"fixed". Use format="table".'
            )
        if not empty_array:
            if hasattr(value, "T"):
                # ExtensionArrays (1d) may not have transpose.
                value = value.T
                transposed = True

        atom = None
        if self._filters is not None:
            with suppress(ValueError):
                # get the atom for this datatype
                atom = _tables().Atom.from_dtype(value.dtype)

        if atom is not None:
            # We only get here if self._filters is non-None and
            #  the Atom.from_dtype call succeeded

            # create an empty chunked array and fill it from value
            if not empty_array:
                ca = self._handle.create_carray(
                    self.group, key, atom, value.shape, filters=self._filters
                )
                ca[:] = value

            else:
                self.write_array_empty(key, value)

        elif value.dtype.type == np.object_:
            # infer the type, warn if we have a non-string type here (for
            # performance)
            inferred_type = lib.infer_dtype(value, skipna=False)
            if empty_array:
                pass
            elif inferred_type == "string":
                pass
            else:
                ws = performance_doc % (inferred_type, key, items)
                warnings.warn(ws, PerformanceWarning, stacklevel=7)

            vlarr = self._handle.create_vlarray(self.group, key, _tables().ObjectAtom())
            vlarr.append(value)

        elif is_datetime64_dtype(value.dtype):
            self._handle.create_array(self.group, key, value.view("i8"))
            getattr(self.group, key)._v_attrs.value_type = "datetime64"
        elif is_datetime64tz_dtype(value.dtype):
            # store as UTC
            # with a zone
            self._handle.create_array(self.group, key, value.asi8)

            node = getattr(self.group, key)
            node._v_attrs.tz = _get_tz(value.tz)
            node._v_attrs.value_type = "datetime64"
        elif is_timedelta64_dtype(value.dtype):
            self._handle.create_array(self.group, key, value.view("i8"))
            getattr(self.group, key)._v_attrs.value_type = "timedelta64"
        elif empty_array:
            self.write_array_empty(key, value)
        else:
            self._handle.create_array(self.group, key, value)

        getattr(self.group, key)._v_attrs.transposed = transposed