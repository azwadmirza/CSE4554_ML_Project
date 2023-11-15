    def _get_stat(self, dim):
        stat_kwargs = {}

        if self.source is not None:
            stat_kwargs['source'] = self.source

            if len(self.dimensions.keys()) > 0:
                stat_kwargs['column'] = self.dimensions[dim]
            elif self.column is not None:
                stat_kwargs['column'] = self.column
            else:
                stat_kwargs['column'] = 'values'
        elif self.values is not None:
            stat_kwargs['values'] = self.values
        else:
            raise ValueError('Could not identify bin stat for %s' % dim)

        #if list(self.dimensions.keys()):
        #    stat_kwargs['bin_count'] = self.bin_count[idx]

        return BinStats(**stat_kwargs)