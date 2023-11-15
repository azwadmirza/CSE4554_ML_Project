    def _process(self, dryrun, msg, show):
        if msg:
            msg = MessageFactory.serialize(self.arg2msg(msg))
            if not self.instance._Bot__source_pipeline:
                # is None if source pipeline does not exist
                self.instance._Bot__source_pipeline = Pipeline(None)
            self.instance._Bot__source_pipeline.receive = lambda *args, **kwargs: msg
            self.instance._Bot__source_pipeline.acknowledge = lambda *args, **kwargs: None
            self.instance.logger.info(" * Message from cli will be used when processing.")

        if dryrun:
            self.instance.send_message = lambda *args, **kwargs: self.instance.logger.info(
                "DRYRUN: Message would be sent now to %r!",
                kwargs.get('path', "_default"))
            self.instance.acknowledge_message = lambda *args, **kwargs: self.instance.logger.info(
                "DRYRUN: Message would be acknowledged now!")
            self.instance.logger.info(" * Dryrun only, no message will be really sent through.")

        if show:
            fn = self.instance.send_message
            self.instance.send_message = lambda *args, **kwargs: [self.pprint(args or "No message generated"),
                                                                  fn(*args, **kwargs)]

        self.instance.logger.info("Processing...")
        self.instance.process()