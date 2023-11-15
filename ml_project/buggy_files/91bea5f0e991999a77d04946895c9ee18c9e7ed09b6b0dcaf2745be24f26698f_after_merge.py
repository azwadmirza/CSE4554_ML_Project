    def process(self, asgs):
        tags = self.get_tag_set()
        error = None

        client = self.get_client()
        with self.executor_factory(max_workers=2) as w:
            futures = {}
            for asg_set in chunks(asgs, self.batch_size):
                futures[w.submit(
                    self.process_resource_set, client, asg_set, tags)] = asg_set
            for f in as_completed(futures):
                asg_set = futures[f]
                if f.exception():
                    self.log.exception(
                        "Exception tagging tag:%s error:%s asg:%s" % (
                            tags,
                            f.exception(),
                            ", ".join([a['AutoScalingGroupName']
                                       for a in asg_set])))
        if error:
            raise error