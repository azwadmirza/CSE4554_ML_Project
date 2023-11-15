        def module_get_(nn_self):
            """overloads torch.nn instances with get method so that parameters could be sent back to owner"""
            for p in nn_self.parameters():
                p.get_()

            if isinstance(nn_self.forward, Plan):
                nn_self.forward.get()

            return nn_self