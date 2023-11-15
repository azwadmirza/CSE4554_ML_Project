    def __call__(self, engine, logger, event_name):
        if not isinstance(logger, TensorboardLogger):
            raise RuntimeError("Handler 'GradsHistHandler' works only with TensorboardLogger")

        global_step = engine.state.get_event_attrib_value(event_name)
        for name, p in self.model.named_parameters():
            if p.grad is None:
                continue

            name = name.replace('.', '/')
            logger.writer.add_histogram(tag="grads/{}".format(name),
                                        values=p.grad.detach().cpu().numpy(),
                                        global_step=global_step)