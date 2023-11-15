        def getattr_impl(context, builder, typ, value):
            sig_args = (typ,)
            sig_kws = {}
            typing_context = context.typing_context
            disp, sig_args = cls._get_dispatcher(typing_context, typ, attr,
                                                 sig_args, sig_kws)
            disp_type = types.Dispatcher(disp)
            sig = disp_type.get_call_type(typing_context, sig_args, sig_kws)
            call = context.get_function(disp_type, sig)
            return call(builder, (value,))