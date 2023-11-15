    def get_launch_id(self, asg):
        lid = asg.get('LaunchConfigurationName')
        if lid is not None:
            # We've noticed trailing white space allowed in some asgs
            return lid.strip()

        lid = asg.get('LaunchTemplate')
        if lid is not None:
            return (lid['LaunchTemplateId'], lid['Version'])

        if 'MixedInstancesPolicy' in asg:
            mip_spec = asg['MixedInstancesPolicy'][
                'LaunchTemplate']['LaunchTemplateSpecification']
            return (mip_spec['LaunchTemplateId'], mip_spec['Version'])

        # we've noticed some corner cases where the asg name is the lc name, but not
        # explicitly specified as launchconfiguration attribute.
        lid = asg['AutoScalingGroupName']
        return lid