    def _add_calibration_datasets(self, ch, datasets, reverse_offset, reverse_scale, decimals):
        _reverse_offset = reverse_offset
        _reverse_scale = reverse_scale
        _decimals = decimals
        _table_calibration = ""
        found_calibration = False
        skip_calibration = False
        for i, ds in enumerate(datasets):
            if 'prerequisites' in ds.attrs and isinstance(ds.attrs['prerequisites'][i], DatasetID):
                if ds.attrs['prerequisites'][i][0] == ch:
                    if ds.attrs['prerequisites'][i][4] == 'RADIANCE':
                        raise NotImplementedError(
                            "Mitiff radiance calibration not implemented.")
                    # _table_calibration += ', Radiance, '
                    # _table_calibration += '[W/m²/µm/sr]'
                    # _decimals = 8
                    elif ds.attrs['prerequisites'][i][4] == 'brightness_temperature':
                        found_calibration = True
                        _table_calibration += ', BT, '
                        _table_calibration += u'\u00B0'  # '\u2103'
                        _table_calibration += u'[C]'

                        _reverse_offset = 255.
                        _reverse_scale = -1.
                        _decimals = 2
                    elif ds.attrs['prerequisites'][i][4] == 'reflectance':
                        found_calibration = True
                        _table_calibration += ', Reflectance(Albedo), '
                        _table_calibration += '[%]'
                        _decimals = 2
                    else:
                        LOG.warning("Unknown calib type. Must be Radiance, Reflectance or BT.")

                        break
                else:
                    continue
            else:
                _table_calibration = ""
                skip_calibration = True
                break
        if not found_calibration:
            _table_calibration = ""
            skip_calibration = True
            # How to format string by passing the format
            # http://stackoverflow.com/questions/1598579/rounding-decimals-with-new-python-format-function
        return skip_calibration, _table_calibration, _reverse_offset, _reverse_scale, _decimals