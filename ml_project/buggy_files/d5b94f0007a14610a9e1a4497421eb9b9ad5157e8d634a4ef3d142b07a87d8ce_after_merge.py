    def record(self, value: float, tags: dict = None) -> None:
        """Record the metric point of the metric.

        Args:
            value(float): The value to be recorded as a metric point.
        """
        assert self._metric is not None
        if tags is not None:
            for val in tags.values():
                if not isinstance(val, str):
                    raise TypeError(
                        f"Tag values must be str, got {type(val)}.")

        default_tag_copy = self._default_tags.copy()
        default_tag_copy.update(tags or {})
        self._metric.record(value, tags=default_tag_copy)