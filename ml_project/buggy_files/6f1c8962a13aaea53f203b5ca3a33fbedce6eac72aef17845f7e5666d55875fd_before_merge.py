    def properties(self, properties: Dict[str, np.ndarray]):
        if not isinstance(properties, dict):
            properties = dataframe_to_properties(properties)
        self._properties = self._validate_properties(properties)
        if self._face_color_property and (
            self._face_color_property not in self._properties
        ):
            self._face_color_property = ''
            warnings.warn('property used for face_color dropped')