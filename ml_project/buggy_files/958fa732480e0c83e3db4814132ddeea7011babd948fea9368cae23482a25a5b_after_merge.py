    def get_data(self, latitude, longitude, start, end,
                 vert_level=None, query_variables=None,
                 close_netcdf_data=True, **kwargs):
        """
        Submits a query to the UNIDATA servers using Siphon NCSS and
        converts the netcdf data to a pandas DataFrame.

        Parameters
        ----------
        latitude: float
            The latitude value.
        longitude: float
            The longitude value.
        start: datetime or timestamp
            The start time.
        end: datetime or timestamp
            The end time.
        vert_level: None, float or integer, default None
            Vertical altitude of interest.
        query_variables: None or list, default None
            If None, uses self.variables.
        close_netcdf_data: bool, default True
            Controls if the temporary netcdf data file should be closed.
            Set to False to access the raw data.
        **kwargs:
            Additional keyword arguments are silently ignored.

        Returns
        -------
        forecast_data : DataFrame
            column names are the weather model's variable names.
        """

        if not self.connected:
            self.connect_to_catalog()

        if vert_level is not None:
            self.vert_level = vert_level

        if query_variables is None:
            self.query_variables = list(self.variables.values())
        else:
            self.query_variables = query_variables

        self.latitude = latitude
        self.longitude = longitude
        self.set_query_latlon()  # modifies self.query
        self.set_location(start, latitude, longitude)

        self.start = start
        self.end = end
        self.query.time_range(self.start, self.end)

        if self.vert_level is not None:
            self.query.vertical_level(self.vert_level)

        self.query.variables(*self.query_variables)
        self.query.accept(self.data_format)

        self.netcdf_data = self.ncss.get_data(self.query)

        # might be better to go to xarray here so that we can handle
        # higher dimensional data for more advanced applications
        self.data = self._netcdf2pandas(self.netcdf_data, self.query_variables,
                                        self.start, self.end)

        if close_netcdf_data:
            self.netcdf_data.close()

        return self.data