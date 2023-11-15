    def _hook_variable(self):
        # Overload 'special' methods here
        self._hook_var___new__()
        self._hook_var_contents()
        self._hook_var_owners()

        for attr in dir(torch.autograd.variable.Variable):

            # Conditions for inclusion/exclusion
            if attr in self.exclude + self.var_exclude:
                continue
            lit = getattr(torch.autograd.variable.Variable, attr)
            is_base = attr in dir(object)
            is_desc = inspect.ismethoddescriptor(lit)
            # is_func = isinstance(type(lit), types.FunctionType)
            is_func = isinstance(lit, types.FunctionType)
            try:
                is_service_func = 'HookService' in lit.__qualname__
            except:
                is_service_func = False
            is_old = re.match('old*', attr) is not None

            # Where the overloading happens
            if ((is_desc or (is_func and not is_service_func)) and not is_base and not is_old):
                passer = self._pass_method_args(lit)
                new_attr = self._overload_method(passer)
                setattr(torch.autograd.variable.Variable,
                        'old_{}'.format(attr), lit)
                setattr(torch.autograd.variable.Variable, attr, new_attr)

        self._hook_var_send_()
        self._hook_get_(torch.autograd.variable.Variable)
        self._hook_var_ser()