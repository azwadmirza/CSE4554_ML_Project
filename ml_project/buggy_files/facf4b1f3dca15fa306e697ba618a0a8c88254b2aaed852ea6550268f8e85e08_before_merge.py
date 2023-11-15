    def deep_cleanup(self, testdata_list):
        """
        This function deletes the AWS resources which were not deleted
        by deleting CloudFormation stacks.

        :param testdata_list: List of TestData objects

        """
        for test in testdata_list:
            failed_stack_ids = []
            for stack in test.get_test_stacks():
                if str(stack['status']) == 'DELETE_FAILED':
                    failed_stack_ids.append(stack['StackId'])
            if len(failed_stack_ids) == 0:
                print(PrintMsg.INFO + "All stacks deleted successfully. Deep clean-up not required.")
                continue

            print(PrintMsg.INFO + "Few stacks failed to delete. Collecting resources for deep clean-up.")
            # get test region from the stack id
            stackdata = CommonTools(failed_stack_ids[0]).parse_stack_info()
            region = stackdata['region']
            session = boto3.session.Session(region_name=region)
            s = Reaper(session)

            failed_stacks = CfnResourceTools.get_all_resources(failed_stack_ids, region)
            # print all resources which failed to delete
            if self.verbose:
                print(PrintMsg.DEBUG + "Resources which failed to delete:\n")
                for failed_stack in failed_stacks:
                    print(PrintMsg.DEBUG + "Stack Id: " + failed_stack['stackId'])
                    for res in failed_stack['resources']:
                        print(PrintMsg.DEBUG + "{0} = {1}, {2} = {3}, {4} = {5}".format(
                            '\n\t\tLogicalId',
                            res.get('logicalId'),
                            '\n\t\tPhysicalId',
                            res.get('physicalId'),
                            '\n\t\tType',
                            res.get('resourceType')
                        ))
                s.delete_all(failed_stacks)

        self.delete_autobucket()