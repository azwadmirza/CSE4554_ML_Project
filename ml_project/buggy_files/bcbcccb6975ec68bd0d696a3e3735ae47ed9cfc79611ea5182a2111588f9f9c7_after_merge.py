  def run_program(self, src, filename, maximum_depth):
    """Run the code and return the CFG nodes.

    Args:
      src: The program source code.
      filename: The filename the source is from.
      maximum_depth: Maximum depth to follow call chains.
    Returns:
      A tuple (CFGNode, set) containing the last CFGNode of the program as
        well as all the top-level names defined by it.
    """
    director = directors.Director(
        src, self.errorlog, filename, self.options.disable)
    # This modifies the errorlog passed to the constructor.  Kind of ugly,
    # but there isn't a better way to wire both pieces together.
    self.errorlog.set_error_filter(director.should_report_error)
    self.director = director
    self.filename = filename

    self.maximum_depth = maximum_depth

    code = self.compile_src(src, filename=filename)
    visitor = _FindIgnoredTypeComments(self.director.type_comments)
    pyc.visit(code, visitor)
    for line in visitor.ignored_lines():
      self.errorlog.ignored_type_comment(
          self.filename, line, self.director.type_comments[line][1])

    node = self.root_cfg_node.ConnectNew("init")
    node, f_globals, f_locals, _ = self.run_bytecode(node, code)
    logging.info("Done running bytecode, postprocessing globals")
    # Check for abstract methods on non-abstract classes.
    for val, frames in self.concrete_classes:
      if not val.is_abstract:
        for member in sum((var.data for var in val.members.values()), []):
          if isinstance(member, abstract.Function) and member.is_abstract:
            self.errorlog.ignored_abstractmethod(frames, val.name, member.name)
    for annot in itertools.chain.from_iterable(self.late_annotations.values()):
      # If `annot` has already been resolved, this is a no-op. Otherwise, it
      # contains a real name error that will be logged when we resolve it now.
      annot.resolve(node, f_globals, f_locals)
    self.late_annotations = None  # prevent adding unresolvable annotations
    for func, opcode in self.functions_type_params_check:
      func.signature.check_type_parameter_count(self.simple_stack(opcode))
    assert not self.frames, "Frames left over!"
    log.info("Final node: <%d>%s", node.id, node.name)
    return node, f_globals.members