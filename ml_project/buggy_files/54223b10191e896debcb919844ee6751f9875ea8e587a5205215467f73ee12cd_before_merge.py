    def explode(self):
        """
        Explode muti-part geometries into multiple single geometries.

        Each row containing a multi-part geometry will be split into
        multiple rows with single geometries, thereby increasing the vertical
        size of the GeoDataFrame.

        The index of the input geodataframe is no longer unique and is
        replaced with a multi-index (original index with additional level
        indicating the multiple geometries: a new zero-based index for each
        single part geometry per multi-part geometry).

        Returns
        -------
        GeoDataFrame
            Exploded geodataframe with each single geometry
            as a separate entry in the geodataframe.

        """
        df_copy = self.copy()

        exploded_geom = df_copy.geometry.explode().reset_index(level=-1)
        exploded_index = exploded_geom.columns[0]

        df = pd.concat(
            [df_copy.drop(df_copy._geometry_column_name, axis=1), exploded_geom], axis=1
        )
        # reset to MultiIndex, otherwise df index is only first level of
        # exploded GeoSeries index.
        df.set_index(exploded_index, append=True, inplace=True)
        df.index.names = list(self.index.names) + [None]
        geo_df = df.set_geometry(self._geometry_column_name)
        return geo_df