    def interactive_cli(ctx, config, verbose):
        '''Interactive UI. Also launchable via `khal interactive`.'''
        prepare_context(ctx, config, verbose)
        controllers.interactive(build_collection(ctx), ctx.obj['conf'])