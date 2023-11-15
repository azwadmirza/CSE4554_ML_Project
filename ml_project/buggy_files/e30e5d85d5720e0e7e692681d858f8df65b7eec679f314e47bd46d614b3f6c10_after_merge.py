    def __getitem__(self, aslice):
        """
        Support slicing the UnifiedResponse as a 2D object.

        The first index is to the client and the second index is the records
        returned from those clients.
        """
        # Just a single int as a slice, we are just indexing client.
        if isinstance(aslice, (int, slice)):
            ret = self._list[aslice]

        # Make sure we only have a length two slice.
        elif isinstance(aslice, tuple):
            if len(aslice) > 2:
                raise IndexError("UnifiedResponse objects can only be sliced with one or two indices.")

            # Indexing both client and records, but only for one client.
            if isinstance(aslice[0], int):
                client_resp = self._list[aslice[0]]
                ret = self._handle_record_slice(client_resp, aslice[1])

            # Indexing both client and records for multiple clients.
            else:
                intermediate = self._list[aslice[0]]
                ret = []
                for client_resp in intermediate:
                    resp = self._handle_record_slice(client_resp, aslice[1])
                    ret.append(resp)

        else:
            raise IndexError("UnifiedResponse objects must be sliced with integers.")

        return UnifiedResponse(ret)