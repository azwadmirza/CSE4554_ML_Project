  def _modify__import__calls(self, red_baron):  # noqa: We want __import__ as part of the name.
    for call_node in red_baron.find_all('CallNode'):
      if call_node.previous and call_node.previous.value == '__import__':
        if self._skip(call_node):
          continue

        parent = call_node.parent_find('AtomtrailersNode')
        original = parent.copy()
        first_argument = call_node[0]
        raw_value = self._find_literal_node(parent, first_argument)
        if raw_value:
          value = raw_value.to_python()
          root_package = value.split('.')[0]
          if root_package in self._packages:
            raw_value.replace('{!r}'.format(self._prefix + '.' + value))
            yield original, parent