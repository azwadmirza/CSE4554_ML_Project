    def _parse_key(self, raw_key):
        key_dict = {}
        key_dict['id'] = key_dict['name'] = raw_key.get('KeyId')
        key_dict['arn'] = raw_key.get('KeyArn')
        key_dict['rotation_enabled'] = raw_key['rotation_status']['KeyRotationEnabled'] \
            if 'rotation_status' in raw_key else None

        key_dict['policy'] = raw_key.get('policy')

        if 'metadata' in raw_key:
            key_dict['creation_date'] = raw_key['metadata']['KeyMetadata']['CreationDate'] if \
                raw_key['metadata']['KeyMetadata']['CreationDate'] else None
            key_dict['key_enabled'] = False if raw_key['metadata']['KeyMetadata']['KeyState'] == 'Disabled' else True
            key_dict['description'] = raw_key['metadata']['KeyMetadata']['Description'] if len(
                raw_key['metadata']['KeyMetadata']['Description'].strip()) > 0 else None
            key_dict['origin'] = raw_key['metadata']['KeyMetadata']['Origin'] if len(
                raw_key['metadata']['KeyMetadata']['Origin'].strip()) > 0 else None
            key_dict['key_manager'] = raw_key['metadata']['KeyMetadata']['KeyManager'] if len(
                raw_key['metadata']['KeyMetadata']['KeyManager'].strip()) > 0 else None

        key_dict['aliases'] = {}
        for raw_alias in raw_key.get('aliases', []):
            alias_id, alias = self._parse_alias(raw_alias)
            key_dict['aliases'][alias_id] = alias

        return key_dict['id'], key_dict