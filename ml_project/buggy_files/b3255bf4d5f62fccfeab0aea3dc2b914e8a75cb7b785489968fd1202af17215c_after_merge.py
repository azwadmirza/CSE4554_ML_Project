    def _hook_module(self):
        """Overloading torch.nn.Module with PySyft functionality, the primary module
           responsible for core ML functionality such as Neural network layers and
           loss functions.
           It is important to note that all the operations are actually in-place.
        """
        self.element_iter_dict = {}

        def register_element_iterator(name, func):
            """register an internal element buffer iterator
            """
            if name in self.element_iter_dict.keys():
                return
            self.element_iter_dict[name] = func

        def tensor_iterator(nn_self):
            """adding relavant iterators for the tensor elements"""
            iterators = [
                "parameters",
                "buffers",
            ]  # all the element iterators from nn module should be listed here,
            return [getattr(nn_self, iter) for iter in iterators]

        def module_is_missing_grad(model):
            """Checks if all the parameters in the model have been assigned a gradient"""
            for p in model.parameters():
                if p.grad is None:
                    return True
            return False

        def create_grad_objects(model):
            """Assigns gradient to model parameters if not assigned"""
            for p in model.parameters():
                if p.requires_grad:  # check if the object requires a grad object
                    o = p.sum()
                    o.backward()
                    if p.grad is not None:
                        p.grad -= p.grad

        def module_send_(nn_self, *dest, force_send=False, **kwargs):
            """Overloads torch.nn instances so that they could be sent to other workers"""

            if module_is_missing_grad(nn_self):
                create_grad_objects(nn_self)

            for element_iter in tensor_iterator(nn_self):
                for p in element_iter():
                    p.send_(*dest, **kwargs)

            if isinstance(nn_self.forward, Plan):
                nn_self.forward.send(*dest, force=force_send)

            return nn_self

        self.torch.nn.Module.send = module_send_
        self.torch.nn.Module.send_ = module_send_

        def module_move_(nn_self, destination):

            params = list(nn_self.parameters())
            for p in params:
                p.move_(destination)

        self.torch.nn.Module.move = module_move_

        # def module_end_get_(nn_self):
        #     """Overloads send to remote for torch.nn.Module."""
        #     if module_is_missing_grad(nn_self):
        #         create_grad_objects(nn_self)
        #
        #     for p in nn_self.parameters():
        #         p.end_get()
        #
        #     return nn_self
        #
        # self.torch.nn.Module.end_get = module_end_get_
        #
        # def module_move_(nn_self, dest):
        #     return nn_self.send(dest).end_get()
        #
        # self.torch.nn.Module.move = module_move_

        def module_get_(nn_self):
            """overloads torch.nn instances with get method so that parameters could be sent back to owner"""
            for element_iter in tensor_iterator(nn_self):
                for p in element_iter():
                    p.get_()

            if isinstance(nn_self.forward, Plan):
                nn_self.forward.get()

            return nn_self

        self.torch.nn.Module.get_ = module_get_
        self.torch.nn.Module.get = module_get_

        def module_share_(nn_self, *args, **kwargs):
            """Overloads fix_precision for torch.nn.Module."""
            if module_is_missing_grad(nn_self):
                create_grad_objects(nn_self)

            for element_iter in tensor_iterator(nn_self):
                for p in element_iter():
                    p.share_(*args, **kwargs)

            return nn_self

        self.torch.nn.Module.share_ = module_share_
        self.torch.nn.Module.share = module_share_

        def module_fix_precision_(nn_self, *args, **kwargs):
            """Overloads fix_precision for torch.nn.Module."""
            if module_is_missing_grad(nn_self):
                create_grad_objects(nn_self)

            for element_iter in tensor_iterator(nn_self):
                for p in element_iter():
                    p.fix_precision_(*args, **kwargs)

            return nn_self

        self.torch.nn.Module.fix_precision_ = module_fix_precision_
        self.torch.nn.Module.fix_precision = module_fix_precision_
        self.torch.nn.Module.fix_prec = module_fix_precision_

        def module_float_precision_(nn_self):
            """Overloads float_precision for torch.nn.Module, convert fix_precision
            parameters to normal float parameters"""
            # TODO: add .data and .grad to syft tensors
            # if module_is_missing_grad(nn_self):
            #    create_grad_objects(nn_self)

            for element_iter in tensor_iterator(nn_self):
                for p in element_iter():
                    p.float_precision_()

            return nn_self

        self.torch.nn.Module.float_precision_ = module_float_precision_
        self.torch.nn.Module.float_precision = module_float_precision_
        self.torch.nn.Module.float_prec = module_float_precision_

        def module_copy(nn_self):
            """Returns a copy of a torch.nn.Module"""
            return copy.deepcopy(nn_self)

        self.torch.nn.Module.copy = module_copy

        @property
        def owner(nn_self):
            for p in nn_self.parameters():
                return p.owner

        self.torch.nn.Module.owner = owner

        @property
        def location(nn_self):
            try:
                for p in nn_self.parameters():
                    return p.location
            except AttributeError:
                raise AttributeError(
                    "Module has no attribute location, did you already send it to some location?"
                )

        self.torch.nn.Module.location = location

        # Make sure PySyft uses the PyTorch version
        self.torch.nn.modules.rnn._rnn_impls["LSTM"] = self.torch.lstm

        # Add support for GRUs
        self.torch.nn.modules.rnn._rnn_impls["GRU"] = self.torch.gru

        # Override _VF.LSTM_Cell and _VF.GRU_Cell with torch.LSTM_Cell and torch.GRU_Cell
        # With the pytorch-based version
        self.torch.nn.modules.rnn._VF = self.torch