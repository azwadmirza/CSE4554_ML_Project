    def load_resource(self, item):
        resource = super(ConfigS3, self).load_resource(item)
        cfg = item['supplementaryConfiguration']
        # aka standard
        if 'awsRegion' in item and item['awsRegion'] != 'us-east-1':
            resource['Location'] = {'LocationConstraint': item['awsRegion']}

        # owner is under acl per describe
        resource.pop('Owner', None)
        resource['CreationDate'] = parse_date(resource['CreationDate'])

        for k, null_value in S3_CONFIG_SUPPLEMENT_NULL_MAP.items():
            if cfg.get(k) == null_value:
                continue
            method = getattr(self, "handle_%s" % k, None)
            if method is None:
                raise ValueError("unhandled supplementary config %s", k)
                continue
            v = cfg[k]
            if isinstance(cfg[k], six.string_types):
                v = json.loads(cfg[k])
            method(resource, v)

        for el in S3_AUGMENT_TABLE:
            if el[1] not in resource:
                resource[el[1]] = el[2]
        return resource