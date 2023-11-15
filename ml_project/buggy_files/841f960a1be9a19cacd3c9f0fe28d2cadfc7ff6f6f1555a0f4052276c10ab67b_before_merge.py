    def log_text(self, log_name: str, text: str, step: Optional[int] = None) -> None:
        """
        Log text data in Neptune experiments.

        Args:
            log_name: The name of log, i.e. mse, my_text_data, timing_info.
            text: The value of the log (data-point).
            step: Step number at which the metrics should be recorded, must be strictly increasing
        """
        self.log_metric(log_name, text, step=step)