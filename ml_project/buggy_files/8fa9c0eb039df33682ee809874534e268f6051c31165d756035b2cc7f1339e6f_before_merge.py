    def images(self, **kwargs):
        """
        Get all of the images for a particular collection by collection id.
        
        Args:
            language: (optional) ISO 639-1 code.
            append_to_response: (optional) Comma separated, any movie method.
            include_image_language: (optional) Comma separated, a valid 
            ISO 69-1. 

        Returns:
            A dict respresentation of the JSON returned from the API.
        """
        path = self._get_id_path('info')

        response = self._GET(path, kwargs)
        self._set_attrs_to_values(response)
        return response