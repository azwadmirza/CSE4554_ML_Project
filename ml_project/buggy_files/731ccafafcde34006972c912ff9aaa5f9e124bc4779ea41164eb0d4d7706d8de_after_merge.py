def infer_attribute(self, context=None):
    """infer an Attribute node by using getattr on the associated object"""
    for owner in self.expr.infer(context):
        if owner is util.Uninferable:
            yield owner
            continue

        if context and context.boundnode:
            # This handles the situation where the attribute is accessed through a subclass
            # of a base class and the attribute is defined at the base class's level,
            # by taking in consideration a redefinition in the subclass.
            if isinstance(owner, bases.Instance) and isinstance(
                context.boundnode, bases.Instance
            ):
                try:
                    if helpers.is_subtype(
                        helpers.object_type(context.boundnode),
                        helpers.object_type(owner),
                    ):
                        owner = context.boundnode
                except exceptions._NonDeducibleTypeHierarchy:
                    # Can't determine anything useful.
                    pass
        elif not context:
            context = contextmod.InferenceContext()

        try:
            context.boundnode = owner
            yield from owner.igetattr(self.attrname, context)
        except (
            exceptions.AttributeInferenceError,
            exceptions.InferenceError,
            AttributeError,
        ):
            pass
        finally:
            context.boundnode = None
    return dict(node=self, context=context)