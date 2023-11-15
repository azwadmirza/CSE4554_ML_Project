    def forward(self, x1, x2):
        covar_i = self.task_covar_module.covar_matrix
        covar_x = self.data_covar_module(x1, x2)
        if covar_x.size(0) == 1:
            covar_x = covar_x[0]
        if not isinstance(covar_x, LazyTensor):
            covar_x = NonLazyTensor(covar_x)
        res = KroneckerProductLazyTensor(covar_i, covar_x)
        return res