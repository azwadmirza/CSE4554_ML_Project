        def create_hierarchy(cat_hierarchy, parent=None):
            """Create category hierarchy."""
            result = []
            for name, children in cat_hierarchy.items():
                node = hierarchy_utils.TreeNode(name, parent)
                node.children = create_hierarchy(children, node)
                node.category_path = [pn.name for pn in node.get_path()]
                node.category_name = self.category_path_to_category_name(node.category_path)
                self.category_hierarchy_lookup[node.category_name] = node
                if node.category_name not in self.config.get('HIDDEN_CATEGORIES'):
                    result.append(node)
            return natsort.natsorted(result, key=lambda e: e.name, alg=natsort.ns.F | natsort.ns.IC)