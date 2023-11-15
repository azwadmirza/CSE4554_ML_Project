        def module_float_precision_(nn_self):
            """Overloads float_precision for torch.nn.Module, convert fix_precision
            parameters to normal float parameters"""
            # TODO: add .data and .grad to syft tensors
            # if module_is_missing_grad(nn_self):
            #    create_grad_objects(nn_self)

            for p in nn_self.parameters():
                p.float_precision_()

            return nn_self