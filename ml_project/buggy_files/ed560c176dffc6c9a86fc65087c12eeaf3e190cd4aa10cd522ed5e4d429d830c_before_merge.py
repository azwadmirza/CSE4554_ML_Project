    def check_mapping_str_interpolation(self, specifiers: List[ConversionSpecifier],
                                        replacements: Expression,
                                        expr: FormatStringExpr) -> None:
        if (isinstance(replacements, DictExpr) and
                all(isinstance(k, (StrExpr, BytesExpr))
                    for k, v in replacements.items)):
            mapping = {}  # type: Dict[str, Type]
            for k, v in replacements.items:
                key_str = cast(StrExpr, k).value
                mapping[key_str] = self.accept(v)

            for specifier in specifiers:
                if specifier.type == '%':
                    # %% is allowed in mappings, no checking is required
                    continue
                assert specifier.key is not None
                if specifier.key not in mapping:
                    self.msg.key_not_in_mapping(specifier.key, replacements)
                    return
                rep_type = mapping[specifier.key]
                expected_type = self.conversion_type(specifier.type, replacements, expr)
                if expected_type is None:
                    return
                self.chk.check_subtype(rep_type, expected_type, replacements,
                                       message_registry.INCOMPATIBLE_TYPES_IN_STR_INTERPOLATION,
                                       'expression has type',
                                       'placeholder with key \'%s\' has type' % specifier.key)
        else:
            rep_type = self.accept(replacements)
            any_type = AnyType(TypeOfAny.special_form)
            dict_type = self.chk.named_generic_type('builtins.dict',
                                                    [any_type, any_type])
            self.chk.check_subtype(rep_type, dict_type, replacements,
                                   message_registry.FORMAT_REQUIRES_MAPPING,
                                   'expression has type', 'expected type for mapping is')