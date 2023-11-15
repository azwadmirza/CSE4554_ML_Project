    def validate_arguments(self, args):
        """
        Validates command line arguments using the retrieved information.
        """

        if args.hostname:
            instances = self.opsworks.describe_instances(
                StackId=self._stack['StackId']
            )['Instances']
            if any(args.hostname.lower() == instance['Hostname']
                   for instance in instances):
                raise ValueError(
                    "Invalid hostname: '%s'. Hostnames must be unique within "
                    "a stack." % args.hostname)

        if args.infrastructure_class == 'ec2' and args.local:
            # make sure the regions match
            region = json.loads(urlopen(IDENTITY_URL).read())['region']
            if region != self._stack['Region']:
                raise ValueError(
                    "The stack's and the instance's region must match.")