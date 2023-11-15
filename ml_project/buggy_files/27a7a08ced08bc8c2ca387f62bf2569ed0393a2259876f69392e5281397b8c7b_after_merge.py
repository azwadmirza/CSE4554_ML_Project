    def iterable_item_type(self, instance: Instance) -> Type:
        iterable = map_instance_to_supertype(
            instance,
            self.lookup_typeinfo('typing.Iterable'))
        item_type = iterable.args[0]
        if not isinstance(item_type, AnyType):
            # This relies on 'map_instance_to_supertype' returning 'Iterable[Any]'
            # in case there is no explicit base class.
            return item_type
        # Try also structural typing.
        iter_type = find_member('__iter__', instance, instance)
        if (iter_type and isinstance(iter_type, CallableType) and
                isinstance(iter_type.ret_type, Instance)):
            iterator = map_instance_to_supertype(iter_type.ret_type,
                                                 self.lookup_typeinfo('typing.Iterator'))
            item_type = iterator.args[0]
        return item_type