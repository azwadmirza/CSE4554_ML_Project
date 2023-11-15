    def __init__(self, values=None, column=None, dimensions=None, bins=None,
                 stat='count', source=None, **properties):
        if isinstance(stat, str):
            stat = stats[stat]()

        # explicit dimensions are handled as extra kwargs
        if dimensions is None:
            dimensions = properties.copy()
            for dim, col in iteritems(properties):
                if not isinstance(col, str):
                    dimensions.pop(dim)
            for dim in list(dimensions.keys()):
                properties.pop(dim)

        bin_count = properties.get('bin_count')
        if bin_count is not None and not isinstance(bin_count, list):
            properties['bin_count'] = [bin_count]
        else:
            properties['bin_count'] = []

        properties['dimensions'] = dimensions
        properties['column'] = column
        properties['bins'] = bins
        properties['stat'] = stat
        properties['values'] = values
        properties['source'] = source

        super(Bins, self).__init__(**properties)