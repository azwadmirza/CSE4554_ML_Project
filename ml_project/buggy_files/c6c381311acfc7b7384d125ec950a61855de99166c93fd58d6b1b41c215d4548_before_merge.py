    def scan_resource_conf(self, conf):
        """
            Looks for password configuration at google_compute_firewall:
            https://www.terraform.io/docs/providers/google/r/compute_firewall.html
        :param conf: azure_instance configuration
        :return: <CheckResult>
        """
        if PORT in conf['allow'][0]['ports'][0]:
            if 'source_ranges' in conf.keys():
                source_ranges = conf['source_ranges'][0]
                if "0.0.0.0/0" in source_ranges:
                    return CheckResult.FAILED
        return CheckResult.PASSED