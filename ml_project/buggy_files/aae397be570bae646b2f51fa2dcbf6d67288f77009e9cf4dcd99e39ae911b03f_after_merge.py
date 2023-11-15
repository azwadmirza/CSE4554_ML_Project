    def __call__(self, projectables, nonprojectables=None, **info):
        if len(projectables) != 3:
            raise ValueError("Expected 3 datasets, got %d" %
                             (len(projectables), ))

        areas = [projectable.attrs.get('area', None)
                 for projectable in projectables]
        areas = [area for area in areas if area is not None]
        if areas and areas.count(areas[0]) != len(areas):
            raise IncompatibleAreas
        try:
            times = [proj['time'][0].values for proj in projectables]
        except KeyError:
            pass
        else:
            # Is there a more gracious way to handle this ?
            if np.max(times) - np.min(times) > np.timedelta64(1, 's'):
                raise IncompatibleTimes
            else:
                mid_time = (np.max(times) - np.min(times)) / 2 + np.min(times)
            projectables[0]['time'] = [mid_time]
            projectables[1]['time'] = [mid_time]
            projectables[2]['time'] = [mid_time]
        try:
            the_data = xr.concat(projectables, 'bands')
            the_data['bands'] = ['R', 'G', 'B']
        except ValueError:
            raise IncompatibleAreas

        attrs = combine_attrs(*projectables)
        attrs.update({key: val
                      for (key, val) in info.items()
                      if val is not None})
        attrs.update(self.attrs)
        # FIXME: should this be done here ?
        attrs["wavelength"] = None
        attrs.pop("units", None)
        sensor = set()
        for projectable in projectables:
            current_sensor = projectable.attrs.get("sensor", None)
            if current_sensor:
                if isinstance(current_sensor, (str, bytes, six.text_type)):
                    sensor.add(current_sensor)
                else:
                    sensor |= current_sensor
        if len(sensor) == 0:
            sensor = None
        elif len(sensor) == 1:
            sensor = list(sensor)[0]
        attrs["sensor"] = sensor
        attrs["mode"] = "RGB"
        the_data.attrs.update(attrs)
        the_data.attrs.pop('resolution', None)
        the_data.attrs.pop('calibration', None)
        the_data.attrs.pop('modifiers', None)
        the_data.name = the_data.attrs['name']

        return the_data