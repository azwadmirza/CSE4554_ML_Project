  def _process_function_type_comment(self, node, op, func):
    """Modifies annotations from a function type comment.

    Checks if a type comment is present for the function.  If so, the type
    comment is used to populate annotations.  It is an error to have
    a type comment when annotations is not empty.

    Args:
      node: The current node.
      op: An opcode (used to determine filename and line number).
      func: An abstract.InterpreterFunction.
    """
    if not op.type_comment:
      return

    comment, lineno = op.type_comment

    # It is an error to use a type comment on an annotated function.
    if func.signature.annotations:
      self.errorlog.redundant_function_type_comment(op.code.co_filename, lineno)
      return

    # Parse the comment, use a fake Opcode that is similar to the original
    # opcode except that it is set to the line number of the type comment.
    # This ensures that errors are printed with an accurate line number.
    fake_stack = self.simple_stack(op.at_line(lineno))
    m = _FUNCTION_TYPE_COMMENT_RE.match(comment)
    if not m:
      self.errorlog.invalid_function_type_comment(fake_stack, comment)
      return
    args, return_type = m.groups()

    if args != "...":
      annot = args.strip()
      try:
        self.annotations_util.eval_multi_arg_annotation(
            node, func, annot, fake_stack)
      except abstract_utils.EvaluationError as e:
        self.errorlog.invalid_function_type_comment(
            fake_stack, annot, details=e.details)
      except abstract_utils.ConversionError:
        self.errorlog.invalid_function_type_comment(
            fake_stack, annot, details="Must be constant.")

    ret = self.convert.build_string(None, return_type)
    func.signature.set_annotation(
        "return", self.annotations_util.process_annotation_var(
            node, ret, "return", fake_stack).data[0])