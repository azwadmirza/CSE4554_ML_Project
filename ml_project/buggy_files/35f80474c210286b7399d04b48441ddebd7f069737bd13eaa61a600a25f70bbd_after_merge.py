    def build_typeddict_typeinfo(self, name: str, items: List[str],
                                 types: List[Type],
                                 required_keys: Set[str]) -> TypeInfo:
        fallback = (self.named_type_or_none('typing.Mapping',
                                            [self.str_type(), self.object_type()])
                    or self.object_type())
        info = self.basic_new_typeinfo(name, fallback)
        info.typeddict_type = TypedDictType(OrderedDict(zip(items, types)), required_keys,
                                            fallback)

        def patch() -> None:
            # Calculate the correct value type for the fallback Mapping.
            assert info.typeddict_type, "TypedDict type deleted before calling the patch"
            fallback.args[1] = join.join_type_list(list(info.typeddict_type.items.values()))

        # We can't calculate the complete fallback type until after semantic
        # analysis, since otherwise MROs might be incomplete. Postpone a callback
        # function that patches the fallback.
        self.patches.append((PRIORITY_FALLBACKS, patch))
        return info