  def decorate(self, node, cls):
    """Processes class members."""

    # Collect classvars to convert them to attrs. @dataclass collects vars with
    # an explicit type annotation, in order of annotation, so that e.g.
    # class A:
    #   x: int
    #   y: str = 'hello'
    #   x = 10
    # would have init(x:int = 10, y:str = 'hello')
    own_attrs = []
    late_annotation = False  # True if we find a bare late annotation
    for name, (value, orig) in self.get_class_locals(
        cls, allow_methods=True, ordering=classgen.Ordering.FIRST_ANNOTATE
    ).items():
      if self.add_member(node, cls, name, value, orig):
        late_annotation = True

      if is_field(orig):
        field = orig.data[0]
        orig = field.typ if field.default else None
        init = field.init
      else:
        init = True

      # Check that default matches the declared type
      if orig and not classgen.is_late_annotation(value):
        typ = self.vm.convert.merge_classes(value.data)
        bad = self.vm.matcher.bad_matches(orig, typ, node)
        if bad:
          binding = bad[0][orig]
          self.vm.errorlog.annotation_type_mismatch(
              self.vm.frames, typ, binding, name)

      attr = classgen.Attribute(name=name, typ=value, init=init, default=orig)
      own_attrs.append(attr)

    # See if we need to resolve any late annotations
    if late_annotation:
      self.vm.classes_with_late_annotations.append(cls)

    base_attrs = self.get_base_class_attrs(
        cls, own_attrs, _DATACLASS_METADATA_KEY)
    attrs = base_attrs + own_attrs
    # Stash attributes in class metadata for subclasses.
    cls.metadata[_DATACLASS_METADATA_KEY] = attrs

    # Add an __init__ method
    if self.args[cls]["init"]:
      init_method = self.make_init(node, cls, attrs)
      cls.members["__init__"] = init_method