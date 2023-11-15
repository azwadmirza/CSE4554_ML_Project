    def _forward_example_input(self) -> None:
        """ Run the example input through each layer to get input- and output sizes. """
        model = self._model
        trainer = self._model.trainer

        input_ = model.example_input_array
        input_ = model.transfer_batch_to_device(input_, model.device)

        if trainer is not None and trainer.use_amp and not trainer.use_tpu:
            if NATIVE_AMP_AVALAIBLE:
                model.forward = torch.cuda.amp.autocast()(model.forward)

        mode = model.training
        model.eval()
        with torch.no_grad():
            # let the model hooks collect the input- and output shapes
            if isinstance(input_, (list, tuple)):
                model(*input_)
            elif isinstance(input_, dict):
                model(**input_)
            else:
                model(input_)
        model.train(mode)  # restore mode of module