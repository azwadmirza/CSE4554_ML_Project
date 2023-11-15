    def process(self, resources):
        client = local_session(self.manager.session_factory).client('iam')

        age = self.data.get('age')
        disable = self.data.get('disable')
        matched = self.data.get('matched')

        if age:
            threshold_date = datetime.datetime.now(tz=tzutc()) - timedelta(age)

        for r in resources:
            if 'c7n:AccessKeys' not in r:
                r['c7n:AccessKeys'] = client.list_access_keys(
                    UserName=r['UserName'])['AccessKeyMetadata']

            keys = r['c7n:AccessKeys']
            if matched:
                m_keys = resolve_credential_keys(
                    r.get(CredentialReport.matched_annotation_key),
                    keys)
                assert m_keys, "shouldn't have gotten this far without keys"
                keys = m_keys

            for k in keys:
                if age:
                    if not k['CreateDate'] < threshold_date:
                        continue
                if disable:
                    client.update_access_key(
                        UserName=r['UserName'],
                        AccessKeyId=k['AccessKeyId'],
                        Status='Inactive')
                else:
                    client.delete_access_key(
                        UserName=r['UserName'],
                        AccessKeyId=k['AccessKeyId'])