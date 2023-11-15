    def begin_epoch(self, epoch):
        """Called at the beginning of each epoch."""
        logger.info("begin training epoch {}".format(epoch))

        if self.quantizer is not None:
            self.quantizer.begin_epoch(epoch)

        # task specific setup per epoch
        self.task.begin_epoch(epoch, self.get_model())

        if self.tpu:
            import torch_xla.core.xla_model as xm

            xm.rendezvous("begin_epoch")  # wait for all workers
            xm.mark_step()