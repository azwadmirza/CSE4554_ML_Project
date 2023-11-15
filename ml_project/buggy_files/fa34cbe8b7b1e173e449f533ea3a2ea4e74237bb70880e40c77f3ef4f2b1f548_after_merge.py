    def _create_new_node(self, current_node, dep_graph, requirement, public_deps, name_req):
        """ creates and adds a new node to the dependency graph
        """
        conanfile_path = self._retriever.get_recipe(requirement.conan_reference)
        output = ScopedOutput(str(requirement.conan_reference), self._output)
        dep_conanfile = self._loader.load_conan(conanfile_path, output)
        if dep_conanfile:
            new_node = Node(requirement.conan_reference, dep_conanfile)
            dep_graph.add_node(new_node)
            dep_graph.add_edge(current_node, new_node)
            if not requirement.private:
                public_deps[name_req] = new_node
            # RECURSION!
            return new_node
        else:
            self._output.error("Could not retrieve %s" % requirement.conan_reference)