    def scan_resource_conf(self, conf):
        """
            Looks for configuration at security group ingress rules :
            https://www.terraform.io/docs/providers/aws/r/security_group.html
        :param conf: aws_security_group configuration
        :return: <CheckResult>
        """
        if 'ingress' in conf.keys():
            ingress_conf = conf['ingress']
            for rule in ingress_conf:
                if rule['from_port'] == [PORT] and rule['to_port'] == [PORT]:
                    if 'cidr_blocks' in rule.keys():
                        if rule['cidr_blocks'] == [["0.0.0.0/0"]] and 'security_groups' not in rule.keys():
                            return CheckResult.FAILED


        return CheckResult.PASSED