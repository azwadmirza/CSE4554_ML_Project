    def get_result(self):
        roots = self.parent_roots

        if len(roots) == 1 and isinstance(roots[0], ops.Selection):
            fused_op = self._check_fusion(roots[0])
            if fused_op is not None:
                return fused_op

        return ops.Selection(self.parent, self.clean_exprs)