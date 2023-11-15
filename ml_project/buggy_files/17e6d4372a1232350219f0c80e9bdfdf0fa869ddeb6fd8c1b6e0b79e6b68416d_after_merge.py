    def __call__(self, engine, logger, event_name):

        if not isinstance(logger, TensorboardLogger):
            raise RuntimeError("Handler 'WeightsScalarHandler' works only with TensorboardLogger")

        global_step = engine.state.get_event_attrib_value(event_name)
        for name, p in self.model.named_parameters():
            if p.grad is None:
                continue

            name = name.replace('.', '/')
            logger.writer.add_scalar("weights_{}/{}".format(self.reduction.__name__, name),
                                     self.reduction(p.data),
                                     global_step)