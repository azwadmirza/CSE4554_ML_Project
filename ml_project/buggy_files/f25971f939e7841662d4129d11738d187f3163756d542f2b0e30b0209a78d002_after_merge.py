        def module_fix_precision_(nn_self, *args, **kwargs):
            """Overloads fix_precision for torch.nn.Module."""
            if module_is_missing_grad(nn_self):
                create_grad_objects(nn_self)

            for element_iter in tensor_iterator(nn_self):
                for p in element_iter():
                    p.fix_precision_(*args, **kwargs)

            return nn_self