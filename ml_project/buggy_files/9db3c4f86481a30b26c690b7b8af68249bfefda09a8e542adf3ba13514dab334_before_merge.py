  def sub_one_annotation(self, node, annot, substs, instantiate_unbound=True):
    """Apply type parameter substitutions to an annotation."""
    if isinstance(annot, abstract.TypeParameter):
      def contains(subst, annot):
        return (annot.full_name in subst and subst[annot.full_name].bindings and
                not any(isinstance(v, abstract.AMBIGUOUS_OR_EMPTY)
                        for v in subst[annot.full_name].data))
      if all(contains(subst, annot) for subst in substs):
        vals = sum((subst[annot.full_name].data for subst in substs), [])
      elif instantiate_unbound:
        vals = annot.instantiate(node).data
      else:
        vals = [annot]
      return self.vm.convert.merge_classes(vals)
    elif isinstance(annot, abstract.ParameterizedClass):
      type_parameters = {
          name: self.sub_one_annotation(
              node, param, substs, instantiate_unbound)
          for name, param in annot.formal_type_parameters.items()}
      # annot may be a subtype of ParameterizedClass, such as TupleClass.
      if isinstance(annot, abstract.LiteralClass):
        # We can't create a LiteralClass because we don't have a concrete value.
        typ = abstract.ParameterizedClass
      else:
        typ = type(annot)
      return typ(annot.base_cls, type_parameters, self.vm, annot.template)
    elif isinstance(annot, abstract.Union):
      options = tuple(self.sub_one_annotation(node, o, substs,
                                              instantiate_unbound)
                      for o in annot.options)
      return type(annot)(options, self.vm)
    return annot