    def _validate_properties(self, properties: Dict[str, np.ndarray]):
        """Validates the type and size of the properties"""
        for k, v in properties.items():
            if len(v) != len(self.data):
                raise ValueError(
                    'the number of properties must equal the number of points'
                )
            # ensure the property values are a numpy array
            if type(v) != np.ndarray:
                properties[k] = np.asarray(v)

        return properties