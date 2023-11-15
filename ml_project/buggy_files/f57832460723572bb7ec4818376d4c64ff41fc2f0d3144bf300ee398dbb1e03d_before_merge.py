    def stackcreate(self, taskcat_cfg, test_list, sprefix):
        """
        This function creates CloudFormation stack for the given tests.

        :param taskcat_cfg: TaskCat config as yaml object
        :param test_list: List of tests
        :param sprefix: Special prefix as string. Purpose of this param is to use it for tagging
            the stack.

        :return: List of TestData objects

        """
        testdata_list = []
        self.set_capabilities('CAPABILITY_NAMED_IAM')
        for test in test_list:
            testdata = TestData()
            testdata.set_test_name(test)
            print(
                "{0}{1}|PREPARING TO LAUNCH => {2}{3}".format(PrintMsg.INFO, PrintMsg.header, test, PrintMsg.rst_color))
            sname = str(sig)

            stackname = sname + '-' + sprefix + '-' + test + '-' + jobid[:8]
            self.define_tests(taskcat_cfg, test)
            for region in self.get_test_region():
                print(PrintMsg.INFO + "Preparing to launch in region [%s] " % region)
                try:
                    cfn = self._boto_client.get('cloudformation', region=region)
                    s_parmsdata = self.get_s3contents(self.get_parameter_path())
                    s_parms = json.loads(s_parmsdata)
                    s_include_params = self.get_param_includes(s_parms)
                    if s_include_params:
                        s_parms = s_include_params
                    j_params = self.generate_input_param_values(s_parms, region)
                    if self.verbose:
                        print(PrintMsg.DEBUG + "Creating Boto Connection region=%s" % region)
                        print(PrintMsg.DEBUG + "StackName=" + stackname)
                        print(PrintMsg.DEBUG + "DisableRollback=True")
                        print(PrintMsg.DEBUG + "TemplateURL=%s" % self.get_template_path())
                        print(PrintMsg.DEBUG + "Capabilities=%s" % self.get_capabilities())
                        print(PrintMsg.DEBUG + "Parameters:")
                        print(PrintMsg.DEBUG + "Tags:%s" % str(self.tags))
                        if self.get_template_type() == 'json':
                            print(json.dumps(j_params, sort_keys=True, indent=11, separators=(',', ': ')))

                    try:
                        stackdata = cfn.create_stack(
                            StackName=stackname,
                            DisableRollback=True,
                            TemplateURL=self.get_template_path(),
                            Parameters=j_params,
                            Capabilities=self.get_capabilities(),
                            Tags=self.tags
                        )
                        print(PrintMsg.INFO + "|CFN Execution mode [create_stack]")
                    except cfn.ecxeptions.ClientError as e:
                        if not str(e).endswith('cannot be used with templates containing Transforms.'):
                            raise
                        print(PrintMsg.INFO + "|CFN Execution mode [change_set]")
                        stack_cs_data = cfn.create_change_set(
                            StackName=stackname,
                            TemplateURL=self.get_template_path(),
                            Parameters=j_params,
                            Capabilities=self.get_capabilities(),
                            ChangeSetType="CREATE",
                            ChangeSetName=stackname + "-cs"
                        )
                        change_set_name = stack_cs_data['Id']

                        # wait for change set
                        waiter = cfn.get_waiter('change_set_create_complete')
                        waiter.wait(
                            ChangeSetName=change_set_name,
                            WaiterConfig={
                                'Delay': 10,
                                'MaxAttempts': 26  # max lambda execute is 5 minutes
                            })

                        cfn.execute_change_set(
                            ChangeSetName=change_set_name
                        )

                        stackdata = {
                            'StackId': stack_cs_data['StackId']
                        }

                    testdata.add_test_stack(stackdata)
                except TaskCatException:
                    raise
                except Exception as e:
                    if self.verbose:
                        print(PrintMsg.ERROR + str(e))
                    raise TaskCatException("Cannot launch %s" % self.get_template_file())

            testdata_list.append(testdata)
        print('\n')
        for test in testdata_list:
            for stack in test.get_test_stacks():
                print("{} |{}LAUNCHING STACKS{}".format(self.nametag, PrintMsg.header, PrintMsg.rst_color))
                print("{} {}{} {} {}".format(
                    PrintMsg.INFO,
                    PrintMsg.header,
                    test.get_test_name(),
                    str(stack['StackId']).split(':stack', 1),
                    PrintMsg.rst_color))
        return testdata_list