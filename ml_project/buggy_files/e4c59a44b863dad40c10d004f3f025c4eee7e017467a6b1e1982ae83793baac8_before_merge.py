    def _register_hook(self):
        """
        Registers a hook on the module that computes the input- and output size(s)
        on the first forward pass. The hook will remove itself from the module, meaning that
        recursive models will only record their input- and output shapes once.
        """

        def hook(module, inp, out):
            if len(inp) == 1:
                inp = inp[0]
            self._in_size = parse_batch_shape(inp)
            self._out_size = parse_batch_shape(out)
            self._hook_handle.remove()  # hook detaches itself from module

        return self._module.register_forward_hook(hook)