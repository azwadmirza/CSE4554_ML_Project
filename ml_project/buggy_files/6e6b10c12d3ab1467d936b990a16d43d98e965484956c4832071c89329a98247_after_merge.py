    def __call__(self, engine, logger, event_name):
        if not isinstance(logger, TensorboardLogger):
            raise RuntimeError("Handler 'GradsScalarHandler' works only with TensorboardLogger")

        global_step = engine.state.get_event_attrib_value(event_name)
        for name, p in self.model.named_parameters():
            if p.grad is None:
                continue

            name = name.replace('.', '/')
            logger.writer.add_scalar("grads_{}/{}".format(self.reduction.__name__, name),
                                     self.reduction(p.grad),
                                     global_step)