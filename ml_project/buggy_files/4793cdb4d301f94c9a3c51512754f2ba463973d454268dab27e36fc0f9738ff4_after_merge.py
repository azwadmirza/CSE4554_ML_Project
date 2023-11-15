    def __eq__(self, other):
      """Redefine equality to raise to nudge people to use static pattern matching."""
      raise self.make_type_error(
        "enum equality is defined to be an error -- use .resolve_for_enum_variant() instead!")