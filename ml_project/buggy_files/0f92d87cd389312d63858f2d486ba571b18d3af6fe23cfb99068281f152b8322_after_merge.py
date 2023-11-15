    def query_region_async(self, coordinates, radius=0.016666666666667*u.deg,
                           collection=None,
                           get_query_payload=False):
        """
        Queries the CADC for a region around the specified coordinates.

        Parameters
        ----------
        coordinates : str or `astropy.coordinates`.
            coordinates around which to query
        radius : str or `astropy.units.Quantity`.
            the radius of the cone search
        collection: Name of the CADC collection to query, optional
        get_query_payload : bool, optional
            Just return the dict of HTTP request parameters.

        Returns
        -------
        response : `requests.Response`
            The HTTP response returned from the service.
            All async methods should return the raw HTTP response.
        """

        if isinstance(radius, (int, float)):
            warnings.warn('Radius should be of type str or '
                          '`astropy.units.Quantity`')
            radius = radius * u.deg

        request_payload = self._args_to_payload(coordinates=coordinates,
                                                radius=radius,
                                                collection=collection)
        # primarily for debug purposes, but also useful if you want to send
        # someone a URL linking directly to the data
        if get_query_payload:
            return request_payload
        response = self.exec_sync(request_payload['query'])
        return response