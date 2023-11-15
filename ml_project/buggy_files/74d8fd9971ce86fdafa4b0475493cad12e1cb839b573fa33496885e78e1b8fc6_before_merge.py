    def process(self, resources, event=None):
        client = local_session(self.manager.session_factory).client(
            'support', region_name='us-east-1')
        checks = client.describe_trusted_advisor_check_result(
            checkId=self.check_id, language='en')['result']

        region = self.manager.config.region
        checks['flaggedResources'] = [r for r in checks['flaggedResources']
            if r['metadata'][0] == region or (r['metadata'][0] == '-' and region == 'us-east-1')]
        resources[0]['c7n:ServiceLimits'] = checks

        delta = timedelta(self.data.get('refresh_period', 1))
        check_date = parse_date(checks['timestamp'])
        if datetime.now(tz=tzutc()) - delta > check_date:
            client.refresh_trusted_advisor_check(checkId=self.check_id)
        threshold = self.data.get('threshold')

        services = self.data.get('services')
        limits = self.data.get('limits')
        exceeded = []

        for resource in checks['flaggedResources']:
            if threshold is None and resource['status'] == 'ok':
                continue
            limit = dict(zip(self.check_limit, resource['metadata']))
            if services and limit['service'] not in services:
                continue
            if limits and limit['check'] not in limits:
                continue
            limit['status'] = resource['status']
            limit['percentage'] = float(limit['extant'] or 0) / float(
                limit['limit']) * 100
            if threshold and limit['percentage'] < threshold:
                continue
            exceeded.append(limit)
        if exceeded:
            resources[0]['c7n:ServiceLimitsExceeded'] = exceeded
            return resources
        return []