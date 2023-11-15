    def expand_from_file(self, nyan_file):
        """
        Expands the tree from a nyan file.

        :param nyan_file: File with nyan objects.
        :type nyan_file: .convert.export.formats.nyan_file.NyanFile
        """
        current_node = self.root
        fqon = nyan_file.get_fqon()
        node_type = NodeType.FILESYS

        for node_str in fqon:
            if current_node.has_child(node_str):
                # Choose the already created node
                current_node = current_node.get_child(node_str)

            else:
                # Add a new node
                new_node = Node(node_str, node_type, current_node)
                current_node.add_child(new_node)
                current_node = new_node

        # Process fqons of the contained objects
        for nyan_object in nyan_file.nyan_objects:
            self.expand_from_object(nyan_object)