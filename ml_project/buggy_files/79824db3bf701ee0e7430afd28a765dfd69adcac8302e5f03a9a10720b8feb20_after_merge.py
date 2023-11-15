    def render_event_pattern(self):
        event_type = self.data.get('type')
        pattern = self.data.get('pattern')

        payload = {}
        if pattern:
            payload.update(pattern)

        if event_type == 'cloudtrail':
            payload['detail-type'] = ['AWS API Call via CloudTrail']
            self.resolve_cloudtrail_payload(payload)
        if event_type == 'cloudtrail':
            if 'signin.amazonaws.com' in payload['detail']['eventSource']:
                payload['detail-type'] = ['AWS Console Sign In via CloudTrail']
        elif event_type == 'guard-duty':
            payload['source'] = ['aws.guardduty']
            payload['detail-type'] = ['GuardDuty Finding']
            if 'resource-filter' in self.data:
                payload.update({
                    'detail': {'resource': {'resourceType': [self.data['resource-filter']]}}})
        elif event_type == "ec2-instance-state":
            payload['source'] = ['aws.ec2']
            payload['detail-type'] = [
                "EC2 Instance State-change Notification"]
            # Technically could let empty be all events, but likely misconfig
            payload['detail'] = {"state": self.data.get('events', [])}
        elif event_type == "asg-instance-state":
            payload['source'] = ['aws.autoscaling']
            events = []
            for e in self.data.get('events', []):
                events.append(self.ASG_EVENT_MAPPING.get(e, e))
            payload['detail-type'] = events
        elif event_type == 'phd':
            payload['source'] = ['aws.health']
            payload.setdefault('detail', {})
            if self.data.get('events'):
                payload['detail'].update({
                    'eventTypeCode': list(self.data['events'])
                })
            if self.data.get('categories', []):
                payload['detail']['eventTypeCategory'] = self.data['categories']
        elif event_type == 'hub-finding':
            payload['source'] = ['aws.securityhub']
            payload['detail-type'] = ['Security Hub Findings - Imported']
        elif event_type == 'hub-action':
            payload['source'] = ['aws.securityhub']
            payload['detail-type'] = [
                'Security Hub Findings - Custom Action',
                'Security Hub Insight Results']
        elif event_type == 'periodic':
            pass
        else:
            raise ValueError(
                "Unknown lambda event source type: %s" % event_type)
        if not payload:
            return None
        if self.data.get('pattern'):
            payload = merge_dict(payload, self.data['pattern'])
        return json.dumps(payload)