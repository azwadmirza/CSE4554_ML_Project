    def get_location(conn, vm_):
        '''
        Return the node location to use.
        Linode wants a location id, which is an integer, when creating a new VM
        To be flexible, let the user specify any of location id, abbreviation, or
        full name of the location ("Fremont, CA, USA") in the config file)
        '''

        locations = avail_locations(conn)
        # Default to Dallas if not otherwise set
        loc = config.get_cloud_config_value(
            'location', vm_, __opts__, default=2
        )

        # Was this an id that matches something in locations?
        if str(loc) not in [locations[k]['id'] for k in locations]:
            # No, let's try to match it against the full
            # name and the abbreviation and return the id
            for key in locations:
                if str(loc).lower() in (key,
                                        str(locations[key]['id']).lower(),
                                        str(locations[key]['abbreviation']).
                                          lower()):
                    return locations[key]['id']
        else:
            return loc

        # No match.  Return None, cloud provider will
        # use a default or throw an exception
        return None