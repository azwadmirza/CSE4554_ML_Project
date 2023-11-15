    def leave_partial_types(self) -> None:
        """Pop partial type scope.

        Also report errors for variables which still have partial
        types, i.e. we couldn't infer a complete type.
        """
        partial_types = self.partial_types.pop()
        if not self.current_node_deferred:
            for var, context in partial_types.items():
                if (experiments.STRICT_OPTIONAL and
                        isinstance(var.type, PartialType) and var.type.type is None):
                    # None partial type: assume variable is intended to have type None
                    var.type = NoneTyp()
                else:
                    self.msg.fail(messages.NEED_ANNOTATION_FOR_VAR, context)
                    var.type = AnyType()