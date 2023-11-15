    def get_image_list(self, query_result, coordinates, radius):
        """
        Function to map the results of a CADC query into URLs to
        corresponding data and cutouts that can be later downloaded.

        The function uses the IVOA DataLink Service
        (http://www.ivoa.net/documents/DataLink/) implemented at the CADC.
        It works directly with the results produced by `query_region` and
        `query_name` but in principle it can work with other query
        results produced with the Cadc query as long as the results
        contain the 'publisherID' column. This column is part of the
        'caom2.Plane' table.

        Parameters
        ----------
        query_result : A `~astropy.table.Table` object
            Result returned by `query_region` or
            `query_name`. In general, the result of any
            CADC TAP query that contains the 'publisherID'
            column can be used here.
        coordinates : str or `astropy.coordinates`.
            Center of the cutout area.
        radius : str or `astropy.units.Quantity`.
            The radius of the cutout area.

        Returns
        -------
        list : A list of URLs to cutout data.
        """

        if not query_result:
            raise AttributeError('Missing query_result argument')

        parsed_coordinates = commons.parse_coordinates(coordinates).fk5
        ra = parsed_coordinates.ra.degree
        dec = parsed_coordinates.dec.degree
        cutout_params = {'POS': 'CIRCLE {} {} {}'.format(ra, dec, radius)}

        try:
            publisher_ids = query_result['publisherID']
        except KeyError:
            raise AttributeError(
                'publisherID column missing from query_result argument')

        result = []

        # Send datalink requests in batches of 20 publisher ids
        batch_size = 20

        # Iterate through list of sublists to send datalink requests in batches
        for pid_sublist in (publisher_ids[pos:pos + batch_size] for pos in
                            range(0, len(publisher_ids), batch_size)):
            datalink = pyvo.dal.adhoc.DatalinkResults.from_result_url(
                '{}?{}'.format(self.data_link_url,
                               urlencode({'ID': pid_sublist}, True)))
            for service_def in datalink.bysemantics('#cutout'):
                access_url = service_def.access_url.decode('ascii')
                if '/sync' in access_url:
                    service_params = service_def.input_params
                    input_params = {param.name: param.value
                                    for param in service_params if
                                    param.name in ['ID', 'RUNID']}
                    input_params.update(cutout_params)
                    result.append('{}?{}'.format(access_url,
                                                 urlencode(input_params)))

        return result