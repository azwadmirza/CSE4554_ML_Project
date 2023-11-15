    def all_composite_ids(self, sensor_names=None):
        """Get all composite IDs that are configured.

        :return: generator of configured composite names
        """
        if sensor_names is None:
            sensor_names = self.attrs['sensor']
        compositors = []
        # Note if we get compositors from the dep tree then it will include
        # modified composites which we don't want
        for sensor_name in sensor_names:
            compositors.extend(
                self.cpl.compositors.get(sensor_name, {}).keys())
        return sorted(set(compositors))