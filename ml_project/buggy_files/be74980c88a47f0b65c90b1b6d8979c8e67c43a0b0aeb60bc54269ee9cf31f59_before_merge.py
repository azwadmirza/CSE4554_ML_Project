    def scan_resource_conf(self, conf):
        """
            validates iam password policy
            https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy.html
        :param conf: aws_iam_account_password_policy configuration
        :return: <CheckResult>
        """
        key = 'password_reuse_prevention'
        if key in conf.keys():
            if conf[key] >= 24:
                return CheckResult.PASSED
        return CheckResult.FAILED