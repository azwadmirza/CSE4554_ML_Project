  def call(self, node, _, args):
    try:
      name_var, field_names, field_types = self._getargs(node, args)
    except abstract_utils.ConversionError:
      return node, self.vm.new_unsolvable(node)

    try:
      name = abstract_utils.get_atomic_python_constant(name_var)
    except abstract_utils.ConversionError:
      return node, self.vm.new_unsolvable(node)

    try:
      field_names = self._validate_and_rename_args(name, field_names, False)
    except ValueError as e:
      self.vm.errorlog.invalid_namedtuple_arg(self.vm.frames, utils.message(e))
      return node, self.vm.new_unsolvable(node)

    annots = self.vm.annotations_util.convert_annotations_list(
        node, moves.zip(field_names, field_types))
    field_types = [annots.get(field_name, self.vm.convert.unsolvable)
                   for field_name in field_names]
    node, cls_var = self._build_namedtuple(name, field_names, field_types, node)

    self.vm.trace_classdef(cls_var)
    return node, cls_var