            def generic(_, args, kws):
                args = (typ,) + tuple(args)
                sig = self._resolve_impl_sig(typ, attr, args, kws)
                if sig is not None:
                    return sig.as_method()