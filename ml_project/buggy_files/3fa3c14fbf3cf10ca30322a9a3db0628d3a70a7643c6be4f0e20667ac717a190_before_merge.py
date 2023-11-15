    def _validate_properties(self, properties: Dict[str, np.ndarray]):
        """Validates the type and size of the properties"""
        for v in properties.values():
            if len(v) != len(self.data):
                raise ValueError(
                    'the number of properties must equal the number of points'
                )

        return properties