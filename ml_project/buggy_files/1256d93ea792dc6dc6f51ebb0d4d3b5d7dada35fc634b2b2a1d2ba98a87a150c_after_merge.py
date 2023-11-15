    def visit_classdef(self, node):
        """init visit variable _accessed
        """
        self._check_bases_classes(node)
        # if not an exception or a metaclass
        if node.type == 'class' and has_known_bases(node):
            try:
                node.local_attr('__init__')
            except astroid.NotFoundError:
                self.add_message('no-init', args=node, node=node)
        self._check_slots(node)
        self._check_proper_bases(node)
        self._check_consistent_mro(node)