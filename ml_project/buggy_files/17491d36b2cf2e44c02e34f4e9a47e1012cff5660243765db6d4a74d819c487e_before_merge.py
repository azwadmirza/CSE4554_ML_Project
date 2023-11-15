        def module_share_(nn_self, *args, **kwargs):
            """Overloads fix_precision for torch.nn.Module."""
            # TODO: add .data and .grad to syft tensors
            if module_is_missing_grad(nn_self):
                create_grad_objects(nn_self)

            for p in nn_self.parameters():
                p.share_(*args, **kwargs)

            return nn_self