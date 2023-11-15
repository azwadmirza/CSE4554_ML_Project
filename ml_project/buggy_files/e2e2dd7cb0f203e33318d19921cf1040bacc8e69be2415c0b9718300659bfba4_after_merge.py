    def _add_calibration(self, channels, cns, datasets, **kwargs):

        _table_calibration = ""
        skip_calibration = False
        for ch in channels:

            palette = False
            # Make calibration.
            if palette:
                raise NotImplementedError("Mitiff palette saving is not implemented.")
            else:
                _table_calibration += 'Table_calibration: '
                try:
                    _table_calibration += str(
                        self.mitiff_config[kwargs['sensor']][cns.get(ch, ch)]['alias'])
                except KeyError:
                    _table_calibration += str(ch)

                _reverse_offset = 0.
                _reverse_scale = 1.
                _decimals = 2

                skip_calibration, __table_calibration, _reverse_offset, _reverse_scale, _decimals = \
                    self._add_calibration_datasets(ch, datasets, _reverse_offset, _reverse_scale, _decimals)
                _table_calibration += __table_calibration

                if not skip_calibration:
                    _table_calibration += ', 8, [ '
                    for val in range(0, 256):
                        # Comma separated list of values
                        _table_calibration += '{0:.{1}f} '.format((float(self.mitiff_config[
                            kwargs['sensor']][cns.get(ch, ch)]['min-val']) +
                            ((_reverse_offset + _reverse_scale * val) *
                             (float(self.mitiff_config[kwargs['sensor']][cns.get(ch, ch)]['max-val']) -
                             float(self.mitiff_config[kwargs['sensor']][cns.get(ch, ch)]['min-val']))) / 255.),
                            _decimals)
                        # _table_calibration += '0.00000000 '

                    _table_calibration += ']\n\n'
                else:
                    _table_calibration = ""

        return _table_calibration