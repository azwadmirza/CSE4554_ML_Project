    def _convert_obj(self, obj):
        obj = super(PeriodIndexResampler, self)._convert_obj(obj)

        offset = to_offset(self.freq)
        if offset.n > 1:
            if self.kind == 'period':  # pragma: no cover
                print('Warning: multiple of frequency -> timestamps')

            # Cannot have multiple of periods, convert to timestamp
            self.kind = 'timestamp'

        # convert to timestamp
        if not (self.kind is None or self.kind == 'period'):
            obj = obj.to_timestamp(how=self.convention)
        return obj