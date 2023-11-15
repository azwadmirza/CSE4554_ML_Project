        def create_grad_objects(model):
            """Assigns gradient to model parameters if not assigned"""
            for p in model.parameters():
                if p.requires_grad:  # check if the object requires a grad object
                    o = p.sum()
                    o.backward()
                    if p.grad is not None:
                        p.grad -= p.grad