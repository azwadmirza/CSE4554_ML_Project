    def get(self, resource_type, identities):
        """Get resources by identities
        """
        m = self.resolve(resource_type)
        params = {}
        client_filter = False

        # Try to formulate server side query
        if m.filter_name:
            if m.filter_type == 'list':
                params[m.filter_name] = identities
            elif m.filter_type == 'scalar':
                assert len(identities) == 1, "Scalar server side filter"
                params[m.filter_name] = identities[0]
        else:
            client_filter = True

        resources = self.filter(resource_type, **params)
        if client_filter:
            # This logic was added to prevent the issue from:
            # https://github.com/capitalone/cloud-custodian/issues/1398
            if all(map(lambda r: isinstance(r, six.string_types), resources)):
                resources = [r for r in resources if r in identities]
            else:
                resources = [r for r in resources if r[m.id] in identities]

        return resources