    def compile(self, sig, locals={}, **targetoptions):
        with self._compile_lock:
            locs = self.locals.copy()
            locs.update(locals)

            topt = self.targetoptions.copy()
            topt.update(targetoptions)

            flags = compiler.Flags()
            self.targetdescr.options.parse_as_flags(flags, topt)

            args, return_type = sigutils.normalize_signature(sig)

            # Don't recompile if signature already exist.
            existing = self.overloads.get(tuple(args))
            if existing is not None:
                return existing

            cres = compiler.compile_extra(self.typingctx, self.targetctx,
                                          self.py_func,
                                          args=args, return_type=return_type,
                                          flags=flags, locals=locs)

            # Check typing error if object mode is used
            if cres.typing_error is not None and not flags.enable_pyobject:
                raise cres.typing_error

            self.add_overload(cres)
            return cres.entry_point