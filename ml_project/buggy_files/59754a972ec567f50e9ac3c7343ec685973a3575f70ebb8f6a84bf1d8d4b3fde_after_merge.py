    def process_asg(self, asg):
        instance_ids = [i['InstanceId'] for i in asg['Instances']]
        tag_map = {t['Key']: t['Value'] for t in asg.get('Tags', [])
                   if t['PropagateAtLaunch'] and not t['Key'].startswith('aws:')}

        if self.data.get('tags'):
            tag_map = {
                k: v for k, v in tag_map.items()
                if k in self.data['tags']}

        if not tag_map and not self.get('trim', False):
            self.log.error(
                'No tags found to propagate on asg:{} tags configured:{}'.format(
                    asg['AutoScalingGroupName'], self.data.get('tags')))

        tag_set = set(tag_map)
        client = local_session(self.manager.session_factory).client('ec2')

        if self.data.get('trim', False):
            instances = [self.instance_map[i] for i in instance_ids]
            self.prune_instance_tags(client, asg, tag_set, instances)

        if not self.manager.config.dryrun and instance_ids and tag_map:
            client.create_tags(
                Resources=instance_ids,
                Tags=[{'Key': k, 'Value': v} for k, v in tag_map.items()])
        return len(instance_ids)