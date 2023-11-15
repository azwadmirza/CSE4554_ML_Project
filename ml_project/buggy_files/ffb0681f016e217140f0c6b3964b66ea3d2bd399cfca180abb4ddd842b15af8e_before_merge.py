    def format_metrics(self, logs={}, factor=1):
        """Format metrics in logs into a string.

        Arguments:
            logs: dictionary of metrics and their values. Defaults to
                empty dictionary.
            factor (int): The factor we want to divide the metrics in logs
                by, useful when we are computing the logs after each batch.
                Defaults to 1.

        Returns:
            metrics_string: a string displaying metrics using the given
            formators passed in through the constructor.
        """

        metric_value_pairs = []
        for metric in self.metrics:
            if metric in logs:
                value = logs[metric] / factor
                pair = self.metrics_format.format(name=metric, value=value)
                metric_value_pairs.append(pair)
        metrics_string = self.metrics_separator.join(metric_value_pairs)
        return metrics_string