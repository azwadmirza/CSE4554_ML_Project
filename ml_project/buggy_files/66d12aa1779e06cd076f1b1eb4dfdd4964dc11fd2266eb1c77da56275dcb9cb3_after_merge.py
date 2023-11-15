def create_proxied_attribute(descriptor):
    """Create an QueryableAttribute / user descriptor hybrid.

    Returns a new QueryableAttribute type that delegates descriptor
    behavior and getattr() to the given descriptor.
    """

    # TODO: can move this to descriptor_props if the need for this
    # function is removed from ext/hybrid.py

    class Proxy(QueryableAttribute):
        """Presents the :class:`.QueryableAttribute` interface as a
        proxy on top of a Python descriptor / :class:`.PropComparator`
        combination.

        """

        def __init__(
            self,
            class_,
            key,
            descriptor,
            comparator,
            adapt_to_entity=None,
            doc=None,
            original_property=None,
        ):
            self.class_ = class_
            self.key = key
            self.descriptor = descriptor
            self.original_property = original_property
            self._comparator = comparator
            self._adapt_to_entity = adapt_to_entity
            self.__doc__ = doc

        _is_internal_proxy = True

        @property
        def _impl_uses_objects(self):
            return (
                self.original_property is not None
                and getattr(self.class_, self.key).impl.uses_objects
            )

        @property
        def property(self):
            return self.comparator.property

        @util.memoized_property
        def comparator(self):
            if util.callable(self._comparator):
                self._comparator = self._comparator()
            if self._adapt_to_entity:
                self._comparator = self._comparator.adapt_to_entity(
                    self._adapt_to_entity
                )
            return self._comparator

        def adapt_to_entity(self, adapt_to_entity):
            return self.__class__(
                adapt_to_entity.entity,
                self.key,
                self.descriptor,
                self._comparator,
                adapt_to_entity,
            )

        def __get__(self, instance, owner):
            retval = self.descriptor.__get__(instance, owner)
            # detect if this is a plain Python @property, which just returns
            # itself for class level access.  If so, then return us.
            # Otherwise, return the object returned by the descriptor.
            if retval is self.descriptor and instance is None:
                return self
            else:
                return retval

        def __str__(self):
            return "%s.%s" % (self.class_.__name__, self.key)

        def __getattr__(self, attribute):
            """Delegate __getattr__ to the original descriptor and/or
            comparator."""
            try:
                return getattr(descriptor, attribute)
            except AttributeError:
                if attribute == "comparator":
                    raise AttributeError("comparator")
                try:
                    # comparator itself might be unreachable
                    comparator = self.comparator
                except AttributeError:
                    raise AttributeError(
                        "Neither %r object nor unconfigured comparator "
                        "object associated with %s has an attribute %r"
                        % (type(descriptor).__name__, self, attribute)
                    )
                else:
                    try:
                        return getattr(comparator, attribute)
                    except AttributeError:
                        raise AttributeError(
                            "Neither %r object nor %r object "
                            "associated with %s has an attribute %r"
                            % (
                                type(descriptor).__name__,
                                type(comparator).__name__,
                                self,
                                attribute,
                            )
                        )

    Proxy.__name__ = type(descriptor).__name__ + "Proxy"

    util.monkeypatch_proxied_specials(
        Proxy, type(descriptor), name="descriptor", from_instance=descriptor
    )
    return Proxy