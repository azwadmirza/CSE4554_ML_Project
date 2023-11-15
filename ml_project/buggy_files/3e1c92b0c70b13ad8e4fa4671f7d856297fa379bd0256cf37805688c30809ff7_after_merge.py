                    def create_hierarchy(hierarchy, parent=None, level=0):
                        """Create hierarchy."""
                        result = {}
                        for name, children in hierarchy.items():
                            node = hierarchy_utils.TreeNode(name, parent)
                            node.children = create_hierarchy(children, node, level + 1)
                            node.classification_path = [pn.name for pn in node.get_path()]
                            node.classification_name = taxonomy.recombine_classification_from_hierarchy(node.classification_path)
                            hierarchy_lookup[node.classification_name] = node
                            result[node.name] = node
                        classifications = natsort.natsorted(result.keys(), alg=natsort.ns.F | natsort.ns.IC)
                        taxonomy.sort_classifications(classifications, lang, level=level)
                        return [result[classification] for classification in classifications]