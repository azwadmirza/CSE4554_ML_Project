    def process(self, resources):
        self.id_key = self.manager.get_model().id

        # Move this to policy? / no resources bypasses actions?
        if not len(resources):
            return

        msg_tmpl = self.data.get(
            'msg',
            'Resource does not meet policy: {op}@{action_date}')

        op = self.data.get('op', 'stop')
        tag = self.data.get('tag', DEFAULT_TAG)
        date = self.data.get('days', 4)

        n = datetime.now(tz=tzutc())
        action_date = n + timedelta(days=date)
        msg = msg_tmpl.format(
            op=op, action_date=action_date.strftime('%Y/%m/%d'))

        self.log.info("Tagging %d resources for %s on %s" % (
            len(resources), op, action_date.strftime('%Y/%m/%d')))

        tags = [{'Key': tag, 'Value': msg}]

        with self.executor_factory(max_workers=2) as w:
            futures = []
            for resource_set in utils.chunks(resources, size=self.batch_size):
                futures.append(
                    w.submit(self.process_resource_set, resource_set, tags))

            for f in as_completed(futures):
                if f.exception():
                    self.log.error(
                        "Exception tagging resource set: %s  \n %s" % (
                            tags, f.exception()))