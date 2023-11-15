    def _rebuild(cls, target_context, libdata, fndesc, env,
                 signature, objectmode, interpmode, lifted, typeann,
                 reload_init):
        if reload_init:
            # Re-run all
            for fn in reload_init:
                fn()

        library = target_context.codegen().unserialize_library(libdata)
        cfunc = target_context.get_executable(library, fndesc, env)
        cr = cls(target_context=target_context,
                 typing_context=target_context.typing_context,
                 library=library,
                 environment=env,
                 entry_point=cfunc,
                 fndesc=fndesc,
                 type_annotation=typeann,
                 signature=signature,
                 objectmode=objectmode,
                 interpmode=interpmode,
                 lifted=lifted,
                 typing_error=None,
                 call_helper=None,
                 metadata=None, # Do not store, arbitrary and potentially large!
                 reload_init=reload_init,
                 )
        return cr