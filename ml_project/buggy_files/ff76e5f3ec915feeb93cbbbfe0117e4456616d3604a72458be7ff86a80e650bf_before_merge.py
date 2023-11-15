    def __init__(self, typingctx, targetctx, library, args, return_type, flags,
                 locals):
        # Make sure the environment is reloaded
        config.reload_config()
        typingctx.refresh()
        targetctx.refresh()

        self.typingctx = typingctx
        self.targetctx = _make_subtarget(targetctx, flags)
        self.library = library
        self.args = args
        self.return_type = return_type
        self.flags = flags
        self.locals = locals

        # Results of various steps of the compilation pipeline
        self.bc = None
        self.func_id = None
        self.func_ir = None
        self.lifted = None
        self.lifted_from = None
        self.typemap = None
        self.calltypes = None
        self.type_annotation = None

        self.status = _CompileStatus(
            can_fallback=self.flags.enable_pyobject,
            can_giveup=config.COMPATIBILITY_MODE
        )