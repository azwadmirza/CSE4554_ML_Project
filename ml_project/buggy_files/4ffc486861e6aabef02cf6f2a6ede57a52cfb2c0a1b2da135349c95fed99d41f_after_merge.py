    def generic(self, args, kws):
        # Redirect resolution to __init__
        instance_type = self.key.instance_type
        ctor = instance_type.jitmethods['__init__']
        boundargs = (instance_type.get_reference_type(),) + args
        disp_type = types.Dispatcher(ctor)
        sig = disp_type.get_call_type(self.context, boundargs, kws)

        if not isinstance(sig.return_type, types.NoneType):
            raise TypeError(
                f"__init__() should return None, not '{sig.return_type}'")

        # Actual constructor returns an instance value (not None)
        out = templates.signature(instance_type, *sig.args[1:])
        return out