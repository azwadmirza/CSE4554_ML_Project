    def get_dmi_facts(self):
        uname_path = self.module.get_bin_path("prtdiag")
        rc, out, err = self.module.run_command(uname_path)
        """
        rc returns 1
        """
        if out:
            system_conf = out.split('\n')[0]
            found = re.search(r'(\w+\sEnterprise\s\w+)',system_conf)
            if found:
                self.facts['product_name'] = found.group(1)