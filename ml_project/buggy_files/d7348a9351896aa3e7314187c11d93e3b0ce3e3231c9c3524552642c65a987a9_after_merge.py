    async def _parse_key(self, raw_key):
        key_dict = {}
        key_dict['id'] = key_dict['name'] = raw_key.get('KeyId')
        key_dict['arn'] = raw_key.get('KeyArn')
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

        # Only call this on customer managed CMKs, otherwise the AWS set policies might disallow access and it's always
        # enabled anyway
        if key_dict['origin'] == 'AWS_KMS' and key_dict['key_manager'] == 'CUSTOMER':
            rotation_status = await self.facade.kms.get_key_rotation_status(self.region, key_dict['id'])
            key_dict['rotation_enabled'] = rotation_status.get('KeyRotationEnabled', None)
        else:
            key_dict['rotation_enabled'] = True

        key_dict['aliases'] = []
        for raw_alias in raw_key.get('aliases', []):
            key_dict['aliases'].append(self._parse_alias(raw_alias))

        return key_dict['id'], key_dict