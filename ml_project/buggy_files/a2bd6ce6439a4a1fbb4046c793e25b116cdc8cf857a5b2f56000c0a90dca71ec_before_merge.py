  def _process_function_type_comment(self, op, annotations, late_annotations):
    """Modifies annotations/late_annotations from a function type comment.

    Checks if a type comment is present for the function.  If so, the type
    comment is used to populate late_annotations.  It is an error to have
    a type comment when annotations or late_annotations is not empty.

    Args:
      op: An opcode (used to determine filename and line number).
      annotations: A dict of annotations.
      late_annotations: A dict of late annotations.
    """
    if not op.type_comment:
      return

    comment, lineno = op.type_comment

    # It is an error to use a type comment on an annotated function.
    if annotations or late_annotations:
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

    # Add type info to late_annotations.
    if args != "...":
      annot = abstract.LateAnnotation(
          args.strip(), function.MULTI_ARG_ANNOTATION, fake_stack)
      late_annotations[function.MULTI_ARG_ANNOTATION] = annot

    ret = self.convert.build_string(None, return_type).data[0]
    late_annotations["return"] = abstract.LateAnnotation(
        ret, "return", fake_stack)