    def save_namedtuple_body(self, named_tuple_info: TypeInfo) -> Iterator[None]:
        """Preserve the generated body of class-based named tuple and then restore it.

        Temporarily clear the names dict so we don't get errors about duplicate names
        that were already set in build_namedtuple_typeinfo (we already added the tuple
        field names while generating the TypeInfo, and actual duplicates are
        already reported).
        """
        nt_names = named_tuple_info.names
        named_tuple_info.names = SymbolTable()

        yield

        # Make sure we didn't use illegal names, then reset the names in the typeinfo.
        for prohibited in NAMEDTUPLE_PROHIBITED_NAMES:
            if prohibited in named_tuple_info.names:
                if nt_names.get(prohibited) is named_tuple_info.names[prohibited]:
                    continue
                ctx = named_tuple_info.names[prohibited].node
                assert ctx is not None
                self.fail('Cannot overwrite NamedTuple attribute "{}"'.format(prohibited),
                          ctx)

        # Restore the names in the original symbol table. This ensures that the symbol
        # table contains the field objects created by build_namedtuple_typeinfo. Exclude
        # __doc__, which can legally be overwritten by the class.
        for key, value in nt_names.items():
            if key in named_tuple_info.names:
                if key == '__doc__':
                    continue
                # Keep existing (user-provided) definitions under mangled names, so they
                # get semantically analyzed.
                r_key = get_unique_redefinition_name(key, named_tuple_info.names)
                named_tuple_info.names[r_key] = named_tuple_info.names[key]
            named_tuple_info.names[key] = value