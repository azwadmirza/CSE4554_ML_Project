    def preprocessing(self, ip_ranges=None, ip_ranges_name_key=None):
        """
        Tweak the AWS config to match cross-service resources and clean any fetching artifacts

        :param ip_ranges:
        :param ip_ranges_name_key:
        :return: None
        """
        ip_ranges = [] if ip_ranges is None else ip_ranges
        self._map_all_sgs()
        self._map_all_subnets()
        self._set_emr_vpc_ids()
        # self.parse_elb_policies()

        # Various data processing calls
        self._check_ec2_zone_distribution()
        self._add_security_group_name_to_ec2_grants()
        self._add_last_snapshot_date_to_ec2_volumes()
        self._process_cloudtrail_trails(self.services['cloudtrail'])
        self._add_cidr_display_name(ip_ranges, ip_ranges_name_key)
        self._merge_route53_and_route53domains()
        self._match_instances_and_roles()
        self._match_iam_policies_and_buckets()

        super(AWSProvider, self).preprocessing()