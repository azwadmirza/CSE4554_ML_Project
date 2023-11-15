    def tv(self, **kwargs):
        """
        Discover TV shows by different types of data like average rating, 
        number of votes, genres, the network they aired on and air dates.

        Args:
            page: (optional) Minimum 1, maximum 1000.
            language: (optional) ISO 639-1 code.
            sort_by: (optional) Available options are 'vote_average.desc', 
                     'vote_average.asc', 'first_air_date.desc', 
                     'first_air_date.asc', 'popularity.desc', 'popularity.asc'
            first_air_year: (optional) Filter the results release dates to 
                            matches that include this value. Expected value 
                            is a year.
            vote_count.gte or vote_count_gte: (optional) Only include TV shows 
                            that are equal to,
                            or have vote count higher than this value. Expected
                            value is an integer.
            vote_average.gte or vote_average_gte: (optional) Only include TV 
                              shows that are equal 
                              to, or have a higher average rating than this 
                              value.  Expected value is a float.
            with_genres: (optional) Only include TV shows with the specified 
                         genres. Expected value is an integer (the id of a 
                         genre).  Multiple valued can be specified. Comma 
                         separated indicates an 'AND' query, while a 
                         pipe (|) separated value indicates an 'OR'.
            with_networks: (optional) Filter TV shows to include a specific 
                           network. Expected value is an integer (the id of a
                           network).  They can be comma separated to indicate an
                           'AND' query.
            first_air_date.gte or first_air_date_gte: (optional) The minimum 
                                release to include. 
                                Expected format is 'YYYY-MM-DD'.
            first_air_date.lte or first_air_date_lte: (optional) The maximum 
                                release to include. 
                                Expected format is 'YYYY-MM-DD'.
          
        Returns:
            A dict respresentation of the JSON returned from the API.
        """
        # Periods are not allowed in keyword arguments but several API 
        # arguments contain periods. See both usages in tests/test_discover.py.
        for param in kwargs:
            if '_lte' in param:
                kwargs[param.replace('_lte', '.lte')] = kwargs.pop(param)
            if '_gte' in param:
                kwargs[param.replace('_gte', '.gte')] = kwargs.pop(param)
        
        path = self._get_path('tv')

        response = self._GET(path, kwargs)
        self._set_attrs_to_values(response)
        return response