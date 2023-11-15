    def _chunk_setitem_nosync(self, chunk_coords, chunk_selection, value, fields=None):

        # obtain key for chunk storage
        ckey = self._chunk_key(chunk_coords)

        if is_total_slice(chunk_selection, self._chunks) and not fields:
            # totally replace chunk

            # optimization: we are completely replacing the chunk, so no need
            # to access the existing chunk data

            if is_scalar(value, self._dtype):

                # setup array filled with value
                chunk = np.empty(self._chunks, dtype=self._dtype, order=self._order)
                chunk.fill(value)

            else:

                if not self._compressor and not self._filters:

                    # https://github.com/alimanfoo/zarr/issues/79
                    # Ensure a copy is taken so we don't end up storing
                    # a view into someone else's array.
                    # N.B., this assumes that filters or compressor always
                    # take a copy and never attempt to apply encoding in-place.
                    chunk = np.array(value, dtype=self._dtype, order=self._order)

                else:
                    # ensure array is contiguous
                    if self._order == 'F':
                        chunk = np.asfortranarray(value, dtype=self._dtype)
                    else:
                        chunk = np.ascontiguousarray(value, dtype=self._dtype)

        else:
            # partially replace the contents of this chunk

            try:

                # obtain compressed data for chunk
                cdata = self.chunk_store[ckey]

            except KeyError:

                # chunk not initialized
                if self._fill_value is not None:
                    chunk = np.empty(self._chunks, dtype=self._dtype, order=self._order)
                    chunk.fill(self._fill_value)
                elif self._dtype == object:
                    chunk = np.empty(self._chunks, dtype=self._dtype, order=self._order)
                else:
                    # N.B., use zeros here so any region beyond the array has consistent
                    # and compressible data
                    chunk = np.zeros(self._chunks, dtype=self._dtype, order=self._order)

            else:

                # decode chunk
                chunk = self._decode_chunk(cdata)
                if not chunk.flags.writeable:
                    chunk = chunk.copy(order='K')

            # modify
            if fields:
                # N.B., currently multi-field assignment is not supported in numpy, so
                # this only works for a single field
                chunk[fields][chunk_selection] = value
            else:
                chunk[chunk_selection] = value

        # encode chunk
        cdata = self._encode_chunk(chunk)

        # store
        self.chunk_store[ckey] = cdata