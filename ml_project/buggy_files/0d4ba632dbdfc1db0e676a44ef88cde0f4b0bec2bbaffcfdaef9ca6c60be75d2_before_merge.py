    def has_different_config(self):
        """
        Return the list of differences between the current parameters and the existing volume.

        :return: list of options that differ
        """
        differences = []
        if self.parameters.driver and self.parameters.driver != self.existing_volume['Driver']:
            differences.append('driver')
        if self.parameters.driver_options:
            if not self.existing_volume.get('Options'):
                differences.append('driver_options')
            else:
                for key, value in iteritems(self.parameters.driver_options):
                    if (not self.existing_volume['Options'].get(key) or
                            value != self.existing_volume['Options'][key]):
                        differences.append('driver_options.%s' % key)
        if self.parameters.labels:
            existing_labels = self.existing_volume.get('Labels', {})
            all_labels = set(self.parameters.labels) | set(existing_labels)
            for label in all_labels:
                if existing_labels.get(label) != self.parameters.labels.get(label):
                    differences.append('labels.%s' % label)

        return differences