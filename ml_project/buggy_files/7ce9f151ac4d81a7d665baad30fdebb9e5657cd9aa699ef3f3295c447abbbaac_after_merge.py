    def get_asg_templates(self, asgs):
        templates = {}
        for a in asgs:
            t = None
            if 'LaunchTemplate' in a:
                t = a['LaunchTemplate']
            elif 'MixedInstancesPolicy' in a:
                t = a['MixedInstancesPolicy'][
                    'LaunchTemplate']['LaunchTemplateSpecification']
            if t is None:
                continue
            templates.setdefault(
                (t['LaunchTemplateId'],
                 t.get('Version', '$Default')), []).append(a['AutoScalingGroupName'])
        return templates