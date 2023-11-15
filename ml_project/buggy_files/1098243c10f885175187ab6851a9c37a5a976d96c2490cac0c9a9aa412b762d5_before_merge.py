    def validate_template(self, taskcat_cfg, test_list):
        """
        Returns TRUE if all the template files are valid, otherwise FALSE.

        :param taskcat_cfg: TaskCat config object
        :param test_list: List of tests

        :return: TRUE if templates are valid, else FALSE
        """
        # Load global regions
        self.set_test_region(self.get_global_region(taskcat_cfg))
        for test in test_list:
            print(self.nametag + " :Validate Template in test[%s]" % test)
            self.define_tests(taskcat_cfg, test)
            try:
                if self.verbose:
                    print(PrintMsg.DEBUG + "Default region [%s]" % self.get_default_region())
                cfn = self._boto_client.get('cloudformation', region=self.get_default_region())

                cfn.validate_template(TemplateURL=self.get_s3_url(self.get_template_file()))
                result = cfn.validate_template(TemplateURL=self.get_s3_url(self.get_template_file()))
                print(PrintMsg.PASS + "Validated [%s]" % self.get_template_file())
                if 'Description' in result:
                    cfn_result = (result['Description'])
                    print(PrintMsg.INFO + "Description  [%s]" % textwrap.fill(cfn_result))
                else:
                    print(
                        PrintMsg.INFO + "Please include a top-level description for template: [%s]" % self.get_template_file())
                if self.verbose:
                    cfn_params = json.dumps(result['Parameters'], indent=11, separators=(',', ': '))
                    print(PrintMsg.DEBUG + "Parameters:")
                    print(cfn_params)
            except TaskCatException:
                raise
            except Exception as e:
                if self.verbose:
                    print(PrintMsg.DEBUG + str(e))
                print(PrintMsg.FAIL + "Cannot validate %s" % self.get_template_file())
                print(PrintMsg.INFO + "Deleting any automatically-created buckets...")
                self.delete_autobucket()
                raise TaskCatException("Cannot validate %s" % self.get_template_file())
        print('\n')
        return True