  def decorate(self, node, cls):
    """Processes the attrib members of a class."""
    # Collect classvars to convert them to attrs.
    if self.args[cls]["auto_attribs"]:
      ordering = classgen.Ordering.FIRST_ANNOTATE
    else:
      ordering = classgen.Ordering.LAST_ASSIGN
    ordered_locals = self.get_class_locals(
        cls, allow_methods=False, ordering=ordering)
    own_attrs = []
    for name, (value, orig) in ordered_locals.items():
      if is_attrib(orig):
        if not is_attrib(value) and orig.data[0].has_type:
          # We cannot have both a type annotation and a type argument.
          self.vm.errorlog.invalid_annotation(self.vm.frames, value.data[0].cls)
          attr = Attribute(
              name=name,
              typ=self.vm.new_unsolvable(node),
              init=orig.data[0].init,
              default=orig.data[0].default)
        else:
          if is_attrib(value):
            # Replace the attrib in the class dict with its type.
            attr = Attribute(
                name=name,
                typ=value.data[0].typ,
                init=value.data[0].init,
                default=value.data[0].default)
            cls.members[name] = attr.typ
          else:
            # cls.members[name] has already been set via a typecomment
            attr = Attribute(
                name=name,
                typ=value,
                init=orig.data[0].init,
                default=orig.data[0].default)
        own_attrs.append(attr)
      elif self.args[cls]["auto_attribs"]:
        # TODO(b/72678203): typing.ClassVar is the only way to filter a variable
        # out from auto_attribs, but we don't even support importing it.
        attr = Attribute(name=name, typ=value, init=True, default=orig)
        cls.members[name] = value
        own_attrs.append(attr)

    base_attrs = self.get_base_class_attrs(cls, own_attrs, _ATTRS_METADATA_KEY)
    attrs = base_attrs + own_attrs
    # Stash attributes in class metadata for subclasses.
    cls.metadata[_ATTRS_METADATA_KEY] = attrs

    # Add an __init__ method
    if self.args[cls]["init"]:
      init_method = self.make_init(node, cls, attrs)
      cls.members["__init__"] = init_method