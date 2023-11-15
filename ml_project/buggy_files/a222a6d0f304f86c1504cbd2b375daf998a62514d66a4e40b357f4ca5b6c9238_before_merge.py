        def create_grad_objects(model):
            """Assigns gradient to model parameters if not assigned"""
            for p in model.parameters():
                o = p.sum()
                o.backward()
                if p.grad is not None:
                    p.grad -= p.grad