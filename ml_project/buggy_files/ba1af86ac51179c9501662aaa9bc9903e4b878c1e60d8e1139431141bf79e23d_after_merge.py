    def _parse_alias(self, raw_alias):
        alias_dict = {
            # all KMS Aliases are prefixed with alias/, so we'll strip that off
            'id': get_non_provider_id(raw_alias.get('AliasArn')),
            'name': raw_alias.get('AliasName').split('alias/', 1)[-1],
            'arn': raw_alias.get('AliasArn'),
            'key_id': raw_alias.get('TargetKeyId')}
        return alias_dict