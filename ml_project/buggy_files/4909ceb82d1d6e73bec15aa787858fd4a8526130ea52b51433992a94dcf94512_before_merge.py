    def process_resource_set(self, client, asgs, tags):
        tag_params = []
        propagate = self.data.get('propagate', False)
        for t in tags:
            if 'PropagateAtLaunch' not in t:
                t['PropagateAtLaunch'] = propagate
        for t in tags:
            for a in asgs:
                atags = dict(t)
                atags['ResourceType'] = 'auto-scaling-group'
                atags['ResourceId'] = a['AutoScalingGroupName']
                tag_params.append(atags)
        self.manager.retry(client.create_or_update_tags, Tags=tag_params)