    def load_resource(self, item):
        resource = super(ConfigTable, self).load_resource(item)
        sse_info = resource.pop('Ssedescription', None)
        if sse_info is None:
            return resource
        resource['SSEDescription'] = sse_info
        for k, r in (('KmsmasterKeyArn', 'KMSMasterKeyArn'),
                     ('Ssetype', 'SSEType')):
            if k in sse_info:
                sse_info[r] = sse_info.pop(k)
        return resource