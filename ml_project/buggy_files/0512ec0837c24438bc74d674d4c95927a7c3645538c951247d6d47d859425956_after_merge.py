    def _args_to_payload(self, *args, **kwargs):
        # convert arguments to a valid requests payload
        # and force the coordinates to FK5 (assuming FK5/ICRS are
        # interchangeable) since RA/Dec are used below
        coordinates = commons.parse_coordinates(kwargs['coordinates']).fk5
        radius_deg = commons.radius_to_unit(kwargs['radius'], unit='degree')
        payload = {format: 'VOTable'}
        payload['query'] = \
            "SELECT * from caom2.Observation o join caom2.Plane p " \
            "ON o.obsID=p.obsID " \
            "WHERE INTERSECTS( " \
            "CIRCLE('ICRS', {}, {}, {}), position_bounds) = 1 AND " \
            "(quality_flag IS NULL OR quality_flag != 'junk')".\
            format(coordinates.ra.degree, coordinates.dec.degree, radius_deg)
        if 'collection' in kwargs and kwargs['collection']:
            payload['query'] = "{} AND collection='{}'".\
                format(payload['query'], kwargs['collection'])
        if 'data_product_type' in kwargs and kwargs['data_product_type']:
            payload['query'] = "{} AND dataProductType='{}'".\
                format(payload['query'], kwargs['data_product_type'])
        return payload