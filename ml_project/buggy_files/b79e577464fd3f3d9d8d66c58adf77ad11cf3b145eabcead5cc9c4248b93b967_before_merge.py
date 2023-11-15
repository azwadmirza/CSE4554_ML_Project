def enum(*args):
  """A datatype which can take on a finite set of values. This method is experimental and unstable.

  Any enum subclass can be constructed with its create() classmethod. This method will use the first
  element of `all_values` as the default value, but enum classes can override this behavior by
  setting `default_value` in the class body.

  NB: Relying on the `field_name` directly is discouraged in favor of using
  resolve_for_enum_variant() in Python code. The `field_name` argument is exposed to make enum
  instances more readable when printed, and to allow code in another language using an FFI to
  reliably extract the value from an enum instance.

  :param string field_name: A string used as the field for the datatype. This positional argument is
                            optional, and defaults to 'value'. Note that `enum()` does not yet
                            support type checking as with `datatype()`.
  :param Iterable all_values: A nonempty iterable of objects representing all possible values for
                              the enum.  This argument must be a finite, non-empty iterable with
                              unique values.
  :raises: :class:`ValueError`
  """
  if len(args) == 1:
    field_name = 'value'
    all_values, = args
  elif len(args) == 2:
    field_name, all_values = args
  else:
    raise ValueError("enum() accepts only 1 or 2 args! args = {!r}".format(args))

  # This call to list() will eagerly evaluate any `all_values` which would otherwise be lazy, such
  # as a generator.
  all_values_realized = list(all_values)
  # `OrderedSet` maintains the order of the input iterable, but is faster to check membership.
  allowed_values_set = OrderedSet(all_values_realized)

  if len(allowed_values_set) == 0:
    raise ValueError("all_values must be a non-empty iterable!")
  elif len(allowed_values_set) < len(all_values_realized):
    raise ValueError("When converting all_values ({}) to a set, at least one duplicate "
                     "was detected. The unique elements of all_values were: {}."
                     .format(all_values_realized, list(allowed_values_set)))

  class ChoiceDatatype(datatype([field_name])):
    default_value = next(iter(allowed_values_set))

    # Overriden from datatype() so providing an invalid variant is catchable as a TypeCheckError,
    # but more specific.
    type_check_error_type = EnumVariantSelectionError

    @memoized_classproperty
    def _singletons(cls):
      """Generate memoized instances of this enum wrapping each of this enum's allowed values.

      NB: The implementation of enum() should use this property as the source of truth for allowed
      values and enum instances from those values.
      """
      return OrderedDict((value, cls._make_singleton(value)) for value in allowed_values_set)

    @classmethod
    def _make_singleton(cls, value):
      """
      We convert uses of the constructor to call create(), so we then need to go around __new__ to
      bootstrap singleton creation from datatype()'s __new__.
      """
      return super(ChoiceDatatype, cls).__new__(cls, value)

    @classproperty
    def _allowed_values(cls):
      """The values provided to the enum() type constructor, for use in error messages."""
      return list(cls._singletons.keys())

    def __new__(cls, value):
      """Forward `value` to the .create() factory method.

      The .create() factory method is preferred, but forwarding the constructor like this allows us
      to use the generated enum type both as a type to check against with isinstance() as well as a
      function to create instances with. This makes it easy to use as a pants option type.
      """
      return cls.create(value)

    @classmethod
    def create(cls, *args, **kwargs):
      """Create an instance of this enum, using the default value if specified.

      :param value: Use this as the enum value. If `value` is an instance of this class, return it,
                    otherwise it is checked against the enum's allowed values. This positional
                    argument is optional, and if not specified, `cls.default_value` is used.
      :param bool none_is_default: If this is True, a None `value` is converted into
                                   `cls.default_value` before being checked against the enum's
                                   allowed values.
      """
      none_is_default = kwargs.pop('none_is_default', False)
      if kwargs:
        raise ValueError('unrecognized keyword arguments for {}.create(): {!r}'
                         .format(cls.__name__, kwargs))

      if len(args) == 0:
        value = cls.default_value
      elif len(args) == 1:
        value = args[0]
        if none_is_default and value is None:
          value = cls.default_value
      else:
        raise ValueError('{}.create() accepts 0 or 1 positional args! *args = {!r}'
                         .format(cls.__name__, args))

      # If we get an instance of this enum class, just return it. This means you can call .create()
      # on an allowed value for the enum, or an existing instance of the enum.
      if isinstance(value, cls):
        return value

      if value not in cls._singletons:
        raise cls.make_type_error(
          "Value {!r} for '{}' must be one of: {!r}."
          .format(value, field_name, cls._allowed_values))
      return cls._singletons[value]

    def resolve_for_enum_variant(self, mapping):
      """Return the object in `mapping` with the key corresponding to the enum value.

      `mapping` is a dict mapping enum variant value -> arbitrary object. All variant values must be
      provided.

      NB: The objects in `mapping` should be made into lambdas if lazy execution is desired, as this
      will "evaluate" all of the values in `mapping`.
      """
      keys = frozenset(mapping.keys())
      if keys != frozenset(self._allowed_values):
        raise self.make_type_error(
          "pattern matching must have exactly the keys {} (was: {})"
          .format(self._allowed_values, list(keys)))
      match_for_variant = mapping[getattr(self, field_name)]
      return match_for_variant

    @classmethod
    def iterate_enum_variants(cls):
      """Iterate over all instances of this enum, in the declared order.

      NB: This method is exposed for testing enum variants easily. resolve_for_enum_variant() should
      be used for performing conditional logic based on an enum instance's value.
      """
      # TODO(#7232): use this method to register attributes on the generated type object for each of
      # the singletons!
      return cls._singletons.values()

  return ChoiceDatatype