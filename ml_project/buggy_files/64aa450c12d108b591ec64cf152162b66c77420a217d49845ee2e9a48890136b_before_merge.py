    def leave_classdef(self, cnode):
        """close a class node:
        check that instance attributes are defined in __init__ and check
        access to existent members
        """
        # check access to existent members on non metaclass classes
        ignore_mixins = get_global_option(self, 'ignore-mixin-members',
                                          default=True)
        if ignore_mixins and cnode.name[-5:].lower() == 'mixin':
            # We are in a mixin class. No need to try to figure out if
            # something is missing, since it is most likely that it will
            # miss.
            return

        accessed = self._accessed.pop()
        if cnode.type != 'metaclass':
            self._check_accessed_members(cnode, accessed)
        # checks attributes are defined in an allowed method such as __init__
        if not self.linter.is_message_enabled('attribute-defined-outside-init'):
            return
        defining_methods = self.config.defining_attr_methods
        current_module = cnode.root()
        for attr, nodes in six.iteritems(cnode.instance_attrs):
            # skip nodes which are not in the current module and it may screw up
            # the output, while it's not worth it
            nodes = [n for n in nodes if not
                     isinstance(n.statement(), (astroid.Delete, astroid.AugAssign))
                     and n.root() is current_module]
            if not nodes:
                continue # error detected by typechecking
            # check if any method attr is defined in is a defining method
            if any(node.frame().name in defining_methods
                   for node in nodes):
                continue

            # check attribute is defined in a parent's __init__
            for parent in cnode.instance_attr_ancestors(attr):
                attr_defined = False
                # check if any parent method attr is defined in is a defining method
                for node in parent.instance_attrs[attr]:
                    if node.frame().name in defining_methods:
                        attr_defined = True
                if attr_defined:
                    # we're done :)
                    break
            else:
                # check attribute is defined as a class attribute
                try:
                    cnode.local_attr(attr)
                except astroid.NotFoundError:
                    for node in nodes:
                        if node.frame().name not in defining_methods:
                            # If the attribute was set by a callfunc in any
                            # of the defining methods, then don't emit
                            # the warning.
                            if _called_in_methods(node.frame(), cnode,
                                                  defining_methods):
                                continue
                            self.add_message('attribute-defined-outside-init',
                                             args=attr, node=node)