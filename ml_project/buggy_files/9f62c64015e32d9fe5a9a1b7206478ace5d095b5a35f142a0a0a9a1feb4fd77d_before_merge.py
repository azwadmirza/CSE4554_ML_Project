        def hook(module, inp, out):
            if len(inp) == 1:
                inp = inp[0]
            self._in_size = parse_batch_shape(inp)
            self._out_size = parse_batch_shape(out)
            self._hook_handle.remove()  # hook detaches itself from module