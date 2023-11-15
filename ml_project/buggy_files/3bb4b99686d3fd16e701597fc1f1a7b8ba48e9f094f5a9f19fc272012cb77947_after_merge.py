    def check_type_var_values(self, type: TypeInfo, actuals: List[Type], arg_name: str,
                              valids: List[Type], arg_number: int, context: Context) -> None:
        for actual in actuals:
            actual = self.update_type(actual)
            if (not isinstance(actual, AnyType) and
                    not any(is_same_type(actual, self.update_type(value)) for value in valids)):
                if len(actuals) > 1 or not isinstance(actual, Instance):
                    self.fail('Invalid type argument value for "{}"'.format(
                        type.name()), context)
                else:
                    class_name = '"{}"'.format(type.name())
                    actual_type_name = '"{}"'.format(actual.type.name())
                    self.fail(messages.INCOMPATIBLE_TYPEVAR_VALUE.format(
                        arg_name, class_name, actual_type_name), context)