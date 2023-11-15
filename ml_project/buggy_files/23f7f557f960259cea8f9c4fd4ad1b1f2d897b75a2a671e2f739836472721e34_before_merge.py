    def create_new_var(self, name: str, typ: Instance) -> Var:
        # type=: type of the variable itself
        var = Var(name=name, type=typ)
        # var.info: type of the object variable is bound to
        var.info = self.model_classdef.info
        var._fullname = self.model_classdef.info.fullname() + '.' + name
        var.is_initialized_in_class = True
        var.is_inferred = True
        return var