    def generic(self, args, kws):
        """
        Type the overloaded function by compiling the appropriate
        implementation for the given args.
        """
        disp, new_args = self._get_impl(args, kws)
        if disp is None:
            return
        # Compile and type it for the given types
        disp_type = types.Dispatcher(disp)
        # Store the compiled overload for use in the lowering phase if there's
        # no inlining required (else functions are being compiled which will
        # never be used as they are inlined)
        if not self._inline.is_never_inline:
            # need to run the compiler front end up to type inference to compute
            # a signature
            from numba.core import typed_passes, compiler
            from numba.core.inline_closurecall import InlineWorker
            fcomp = disp._compiler
            flags = compiler.Flags()

            # Updating these causes problems?!
            #fcomp.targetdescr.options.parse_as_flags(flags,
            #                                         fcomp.targetoptions)
            #flags = fcomp._customize_flags(flags)

            # spoof a compiler pipline like the one that will be in use
            tyctx = fcomp.targetdescr.typing_context
            tgctx = fcomp.targetdescr.target_context
            compiler_inst = fcomp.pipeline_class(tyctx, tgctx, None, None, None,
                                                 flags, None, )
            inline_worker = InlineWorker(tyctx, tgctx, fcomp.locals,
                                         compiler_inst, flags, None,)

            ir = inline_worker.run_untyped_passes(disp_type.dispatcher.py_func)
            resolve = disp_type.dispatcher.get_call_template
            template, pysig, folded_args, kws = resolve(new_args, kws)

            typemap, return_type, calltypes = typed_passes.type_inference_stage(
                self.context, ir, folded_args, None)
            sig = Signature(return_type, folded_args, None)
            # this stores a load of info for the cost model function if supplied
            # it by default is None
            self._inline_overloads[sig.args] = {'folded_args': folded_args}
            # this stores the compiled overloads, if there's no compiled
            # overload available i.e. function is always inlined, the key still
            # needs to exist for type resolution

            # NOTE: If lowering is failing on a `_EmptyImplementationEntry`,
            #       the inliner has failed to inline this entry corretly.
            impl_init = _EmptyImplementationEntry('always inlined')
            self._compiled_overloads[sig.args] = impl_init
            if not self._inline.is_always_inline:
                # this branch is here because a user has supplied a function to
                # determine whether to inline or not. As a result both compiled
                # function and inliner info needed, delaying the computation of
                # this leads to an internal state mess at present. TODO: Fix!
                sig = disp_type.get_call_type(self.context, new_args, kws)
                self._compiled_overloads[sig.args] = disp_type.get_overload(sig)
                # store the inliner information, it's used later in the cost
                # model function call
            iinfo = _inline_info(ir, typemap, calltypes, sig)
            self._inline_overloads[sig.args] = {'folded_args': folded_args,
                                                'iinfo': iinfo}
        else:
            sig = disp_type.get_call_type(self.context, new_args, kws)
            self._compiled_overloads[sig.args] = disp_type.get_overload(sig)
        return sig