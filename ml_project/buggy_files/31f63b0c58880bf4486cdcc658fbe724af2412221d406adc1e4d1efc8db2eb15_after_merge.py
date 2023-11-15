    def as_werkzeug_kwargs(self) -> Dict[str, Any]:
        """Convert the case into a dictionary acceptable by werkzeug.Client."""
        headers = self.headers
        extra: Dict[str, Optional[Union[Dict, bytes]]]
        if self.form_data:
            extra = {"data": self.form_data}
            headers = headers or {}
            headers.setdefault("Content-Type", "multipart/form-data")
        elif is_multipart(self.body):
            extra = {"data": self.body}
        else:
            extra = {"json": self.body}
        return {
            "method": self.method,
            "path": self.formatted_path,
            "headers": headers,
            "query_string": self.query,
            **extra,
        }