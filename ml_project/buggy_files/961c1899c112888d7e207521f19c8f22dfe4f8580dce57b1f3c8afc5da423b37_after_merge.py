    def __init__(self, path):
        super(BadMetricError, self).__init__(
            "'{}' does not exist, not a metric or is malformed".format(
                relpath(path)
            )
        )