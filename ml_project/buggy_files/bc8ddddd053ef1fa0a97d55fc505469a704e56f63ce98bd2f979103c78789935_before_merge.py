    def check_overlapping_op_methods(self,
                                     reverse_type: CallableType,
                                     reverse_name: str,
                                     reverse_class: TypeInfo,
                                     forward_type: Type,
                                     forward_name: str,
                                     forward_base: Instance,
                                     context: Context) -> None:
        """Check for overlapping method and reverse method signatures.

        Assume reverse method has valid argument count and kinds.
        """

        # Reverse operator method that overlaps unsafely with the
        # forward operator method can result in type unsafety. This is
        # similar to overlapping overload variants.
        #
        # This example illustrates the issue:
        #
        #   class X: pass
        #   class A:
        #       def __add__(self, x: X) -> int:
        #           if isinstance(x, X):
        #               return 1
        #           return NotImplemented
        #   class B:
        #       def __radd__(self, x: A) -> str: return 'x'
        #   class C(X, B): pass
        #   def f(b: B) -> None:
        #       A() + b # Result is 1, even though static type seems to be str!
        #   f(C())
        #
        # The reason for the problem is that B and X are overlapping
        # types, and the return types are different. Also, if the type
        # of x in __radd__ would not be A, the methods could be
        # non-overlapping.

        for forward_item in union_items(forward_type):
            if isinstance(forward_item, CallableType):
                # TODO check argument kinds
                if len(forward_item.arg_types) < 1:
                    # Not a valid operator method -- can't succeed anyway.
                    return

                # Construct normalized function signatures corresponding to the
                # operator methods. The first argument is the left operand and the
                # second operand is the right argument -- we switch the order of
                # the arguments of the reverse method.
                forward_tweaked = CallableType(
                    [forward_base, forward_item.arg_types[0]],
                    [nodes.ARG_POS] * 2,
                    [None] * 2,
                    forward_item.ret_type,
                    forward_item.fallback,
                    name=forward_item.name)
                reverse_args = reverse_type.arg_types
                reverse_tweaked = CallableType(
                    [reverse_args[1], reverse_args[0]],
                    [nodes.ARG_POS] * 2,
                    [None] * 2,
                    reverse_type.ret_type,
                    fallback=self.named_type('builtins.function'),
                    name=reverse_type.name)

                if is_unsafe_overlapping_signatures(forward_tweaked,
                                                    reverse_tweaked):
                    self.msg.operator_method_signatures_overlap(
                        reverse_class.name(), reverse_name,
                        forward_base.type.name(), forward_name, context)
            elif isinstance(forward_item, Overloaded):
                for item in forward_item.items():
                    self.check_overlapping_op_methods(
                        reverse_type, reverse_name, reverse_class,
                        item, forward_name, forward_base, context)
            elif not isinstance(forward_item, AnyType):
                self.msg.forward_operator_not_callable(forward_name, context)