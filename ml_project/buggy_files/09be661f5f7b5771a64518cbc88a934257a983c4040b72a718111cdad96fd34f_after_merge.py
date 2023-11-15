    def scan_resource_conf(self, conf):
        """
            validates iam password policy
            https://www.terraform.io/docs/providers/aws/r/iam_account_password_policy.html
        :param conf: aws_iam_account_password_policy configuration
        :return: <CheckResult>
        """
        key = 'max_password_age'
        if key in conf.keys():
            if conf[key][0] >= 90:
                return CheckResult.PASSED
        return CheckResult.FAILED