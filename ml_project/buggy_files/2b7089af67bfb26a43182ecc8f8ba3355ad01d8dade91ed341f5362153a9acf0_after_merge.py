    def validate_parameters(self, taskcat_cfg, test_list):
        """
        This function validates the parameters file of the CloudFormation template.

        :param taskcat_cfg: TaskCat config yaml object
        :param test_list: List of tests

        :return: TRUPrintMsg.ERROR if the parameters file is valid, else FALSE
        """
        for test in test_list:
            self.define_tests(taskcat_cfg, test)
            print(self.nametag + " |Validate JSON input in test[%s]" % test)
            if self.verbose:
                print(PrintMsg.DEBUG + "parameter_path = %s" % self.get_parameter_path())

            inputparms = self.get_contents("./" + self.get_project() + "/ci/" + self.get_parameter_file())
            jsonstatus = self.check_json(inputparms)

            if self.verbose:
                print(PrintMsg.DEBUG + "jsonstatus = %s" % jsonstatus)

            if jsonstatus:
                print(PrintMsg.PASS + "Validated [%s]" % self.get_parameter_file())
            else:
                print(PrintMsg.DEBUG + "parameter_file = %s" % self.get_parameter_file())
                raise TaskCatException("Cannot validate %s" % self.get_parameter_file())
        return True