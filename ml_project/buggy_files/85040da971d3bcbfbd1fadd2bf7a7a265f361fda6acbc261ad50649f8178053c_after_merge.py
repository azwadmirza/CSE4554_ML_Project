    def _compile_core(self, sig, flags, locals):
        """
        Trigger the compiler on the core function or load a previously
        compiled version from the cache.  Returns the CompileResult.
        """
        typingctx = self.targetdescr.typing_context
        targetctx = self.targetdescr.target_context

        @contextmanager
        def store_overloads_on_success():
            # use to ensure overloads are stored on success
            try:
                yield
            except Exception:
                raise
            else:
                exists = self.overloads.get(cres.signature)
                if exists is None:
                    self.overloads[cres.signature] = cres

        # Use cache and compiler in a critical section
        with global_compiler_lock:
            with store_overloads_on_success():
                # attempt look up of existing
                cres = self.cache.load_overload(sig, targetctx)
                if cres is not None:
                    return cres

                # Compile
                args, return_type = sigutils.normalize_signature(sig)
                cres = compiler.compile_extra(typingctx, targetctx,
                                              self.py_func, args=args,
                                              return_type=return_type,
                                              flags=flags, locals=locals)

                # cache lookup failed before so safe to save
                self.cache.save_overload(sig, cres)

                return cres