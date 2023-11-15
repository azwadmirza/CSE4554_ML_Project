    def run(self, event, lambda_context):
        cfg_event = json.loads(event['invokingEvent'])
        resource_type = self.policy.resource_manager.resource_type.cfn_type
        resource_id = self.policy.resource_manager.resource_type.id
        client = self._get_client()

        matched_resources = set()
        for r in PullMode.run(self):
            matched_resources.add(r[resource_id])
        unmatched_resources = set()
        for r in self.policy.resource_manager.get_resource_manager(
                self.policy.resource_type).resources():
            if r[resource_id] not in matched_resources:
                unmatched_resources.add(r[resource_id])

        evaluations = [dict(
            ComplianceResourceType=resource_type,
            ComplianceResourceId=r,
            ComplianceType='NON_COMPLIANT',
            OrderingTimestamp=cfg_event['notificationCreationTime'],
            Annotation='The resource is not compliant with policy:%s.' % (
                self.policy.name))
            for r in matched_resources]
        if evaluations:
            self.policy.resource_manager.retry(
                client.put_evaluations,
                Evaluations=evaluations,
                ResultToken=event.get('resultToken', 'No token found.'))

        evaluations = [dict(
            ComplianceResourceType=resource_type,
            ComplianceResourceId=r,
            ComplianceType='COMPLIANT',
            OrderingTimestamp=cfg_event['notificationCreationTime'],
            Annotation='The resource is compliant with policy:%s.' % (
                self.policy.name))
            for r in unmatched_resources]
        if evaluations:
            self.policy.resource_manager.retry(
                client.put_evaluations,
                Evaluations=evaluations,
                ResultToken=event.get('resultToken', 'No token found.'))
        return list(matched_resources)