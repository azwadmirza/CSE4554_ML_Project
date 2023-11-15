def arguments_assigned_stmts(self, node=None, context=None, asspath=None):
    if context.callcontext:
        # reset call context/name
        callcontext = context.callcontext
        context = contextmod.copy_context(context)
        context.callcontext = None
        args = arguments.CallSite(callcontext)
        return args.infer_argument(self.parent, node.name, context)
    return _arguments_infer_argname(self, node.name, context)