    def _process(self, dryrun, msg, show):
        if msg:
            msg = MessageFactory.serialize(self.arg2msg(msg))
            if not self.instance._Bot__source_pipeline:
                # is None if source pipeline does not exist
                self.instance._Bot__source_pipeline = Pipeline(None)
            self.instance._Bot__source_pipeline.receive = lambda: msg
            self.instance._Bot__source_pipeline.acknowledge = lambda: None
            self.instance.logger.info(" * Message from cli will be used when processing.")

        if dryrun:
            self.instance.send_message = lambda msg, path="_default": self.instance.logger.info(
                "DRYRUN: Message would be sent now{}!".format(" to the {} path".format(path) if (path != "_default") else ""))
            self.instance.acknowledge_message = lambda: self.instance.logger.info("DRYRUN: Message would be acknowledged now!")
            self.instance.logger.info(" * Dryrun only, no message will be really sent through.")

        if show:
            fn = self.instance.send_message
            self.instance.send_message = lambda msg=None, path="_default": [self.pprint(msg or "No message generated"),
                                                                            fn(msg, path=path)]

        self.instance.logger.info("Processing...")
        self.instance.process()