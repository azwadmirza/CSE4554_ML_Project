    def _validate_parameters(self):
        self._confirm_required("name", self.name)
        self._confirm_required("display_name", self.display_name)
        self._confirm_required("api_endpoint", self.api_endpoint)
        self._confirm_required("cos_endpoint", self.cos_endpoint)
        self._confirm_required("cos_bucket", self.cos_bucket)