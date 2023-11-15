    def interactive_cli(ctx):
        '''Interactive UI. Also launchable via `khal interactive`.'''
        controllers.interactive(build_collection(ctx), ctx.obj['conf'])