    def get_call_type(self, context, args, kws):
        failures = _ResolutionFailures(context, self, args, kws)
        for temp_cls in self.templates:
            temp = temp_cls(context)
            for uselit in [True, False]:
                try:
                    if uselit:
                        sig = temp.apply(args, kws)
                    else:
                        nolitargs = tuple([unliteral(a) for a in args])
                        nolitkws = {k: unliteral(v) for k, v in kws.items()}
                        sig = temp.apply(nolitargs, nolitkws)
                except Exception as e:
                    sig = None
                    failures.add_error(temp_cls, e)
                else:
                    if sig is not None:
                        self._impl_keys[sig.args] = temp.get_impl_key(sig)
                        return sig
                    else:
                        haslit= '' if uselit else 'out'
                        msg = "All templates rejected with%s literals." % haslit
                        failures.add_error(temp_cls, msg)

        if len(failures) == 0:
            raise AssertionError("Internal Error. "
                                 "Function resolution ended with no failures "
                                 "or successful signature")
        failures.raise_error()