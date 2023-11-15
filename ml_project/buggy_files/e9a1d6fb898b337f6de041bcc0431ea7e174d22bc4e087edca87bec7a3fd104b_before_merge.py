    def training_step(self, *args, **kwargs):
        """return loss, dict with metrics for tqdm

        :param batch: The output of your dataloader. A tensor, tuple or list
        :param int batch_idx: Integer displaying which batch this is
        :return: dict with loss key and optional log, progress keys
         if implementing training_step, return whatever you need in that step:
            - loss -> tensor scalar [REQUIRED]
            - progress_bar -> Dict for progress bar display. Must have only tensors
            - log -> Dict of metrics to add to logger. Must have only tensors (no images, etc)

        In this step you'd normally do the forward pass and calculate the loss for a batch.
         You can also do fancier things like multiple forward passes or something specific to your model.

        Example
        -------

        .. code-block:: python

            def training_step(self, batch, batch_idx):
                x, y, z = batch

                # implement your own
                out = self.forward(x)
                loss = self.loss(out, x)

                logger_logs = {'training_loss': loss} # optional (MUST ALL BE TENSORS)

                # if using TestTubeLogger or TensorBoardLogger you can nest scalars
                logger_logs = {'losses': logger_logs} # optional (MUST ALL BE TENSORS)

                output = {
                    'loss': loss, # required
                    'progress_bar': {'training_loss': loss}, # optional (MUST ALL BE TENSORS)
                    'log': logger_logs
                }

                # return a dict
                return output

        If you define multiple optimizers, this step will also be called with an additional `optimizer_idx` param.

        .. code-block:: python

            # Multiple optimizers (ie: GANs)
            def training_step(self, batch, batch_idx, optimizer_idx):
                if optimizer_idx == 0:
                    # do training_step with encoder
                if optimizer_idx == 1:
                    # do training_step with decoder


        If you add truncated back propagation through time you will also get an additional
         argument with the hidden states of the previous step.

        .. code-block:: python

            # Truncated back-propagation through time
            def training_step(self, batch, batch_idx, hiddens):
                # hiddens are the hiddens from the previous truncated backprop step

        You can also return a -1 instead of a dict to stop the current loop. This is useful
         if you want to break out of the current training epoch early.
        """