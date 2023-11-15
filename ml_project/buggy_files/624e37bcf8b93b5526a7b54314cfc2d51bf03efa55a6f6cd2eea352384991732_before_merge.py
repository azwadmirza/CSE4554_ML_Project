    def get_alias_fqon(self, fqon):
        """
        Find the (shortened) fqon by traversing the tree to the fqon node and
        then going upwards until a marked node is found.
        """
        # Traverse the tree downwards
        current_node = self.root
        for part in fqon:
            current_node = current_node.get_child(part)

        # Traverse the tree upwards
        sfqon = []
        while current_node.depth > 0:
            sfqon.insert(0, current_node.name)

            if current_node.alias:
                break

            current_node = current_node.parent

        return tuple(sfqon)