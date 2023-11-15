    def record(self, value: float, tags: dict = None) -> None:
        """Record the metric point of the metric.

        Args:
            value(float): The value to be recorded as a metric point.
        """
        assert self._metric is not None
        default_tag_copy = self._default_tags.copy()
        default_tag_copy.update(tags or {})
        self._metric.record(value, tags=default_tag_copy)