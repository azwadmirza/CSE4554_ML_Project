    def get_appelb_target_groups(self):
        manager = self.manager.get_resource_manager('app-elb-target-group')
        return set([a['TargetGroupArn'] for a in manager.resources()])