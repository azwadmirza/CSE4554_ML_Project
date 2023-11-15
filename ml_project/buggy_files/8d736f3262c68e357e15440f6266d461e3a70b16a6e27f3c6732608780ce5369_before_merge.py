    def load_resource(self, item):
        resource = super(ConfigTable, self).load_resource(item)
        resource['CreationDateTime'] = datetime.fromtimestamp(resource['CreationDateTime'] / 1000.0)
        if ('BillingModeSummary' in resource and
                'LastUpdateToPayPerRequestDateTime' in resource['BillingModeSummary']):
            resource['BillingModeSummary'][
                'LastUpdateToPayPerRequestDateTime'] = datetime.fromtimestamp(
                    resource['BillingModeSummary']['LastUpdateToPayPerRequestDateTime'] / 1000.0)

        sse_info = resource.pop('Ssedescription', None)
        if sse_info is None:
            return resource
        resource['SSEDescription'] = sse_info
        for k, r in (('KmsmasterKeyArn', 'KMSMasterKeyArn'),
                     ('Ssetype', 'SSEType')):
            if k in sse_info:
                sse_info[r] = sse_info.pop(k)
        return resource