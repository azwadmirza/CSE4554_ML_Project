    def get_alias_fqon(self, fqon, namespace=None):
        """
        Find the (shortened) fqon by traversing the tree to the fqon node and
        then going upwards until an alias is found.

        :param fqon: Object reference for which an alias should be found.
        :type fqon: tuple
        :param namespace: Identifier of a namespace. If this is a (nested) object,
                          we check if the fqon is in the namespace before
                          searching for an alias.
        :type namespace: tuple
        """
        if namespace:
            current_node = self.root

            if len(namespace) <= len(fqon):
                # Check if the fqon is in the namespace by comparing their identifiers
                for index in range(len(namespace)):
                    current_node = current_node.get_child(namespace[index])

                    if namespace[index] != fqon[index]:
                        break

                else:
                    # Check if the namespace node is an object
                    if current_node.node_type in (NodeType.OBJECT, NodeType.NESTED):
                        # The object with the fqon is nested and we don't have to look
                        # up an alias
                        return (fqon[-1],)

        # Traverse the tree downwards
        current_node = self.root
        for part in fqon:
            current_node = current_node.get_child(part)

        # Traverse the tree upwards
        sfqon = []
        while current_node.depth > 0:
            if current_node.alias:
                sfqon.insert(0, current_node.alias)
                current_node.mark()
                break

            sfqon.insert(0, current_node.name)

            current_node = current_node.parent

        if not current_node.alias:
            print(fqon)

        return tuple(sfqon)