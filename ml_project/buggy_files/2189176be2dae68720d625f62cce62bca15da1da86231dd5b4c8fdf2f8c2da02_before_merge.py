    def generate(input_list, indent_levels_so_far):
        for index, element in enumerate(input_list):
            # add to destination
            elements.append(element)
            # compute and set indent levels
            indent_levels = indent_levels_so_far + [(index, len(input_list))]
            element.indent_levels = indent_levels
            # add children
            children = element.get_children()
            element.children_count = len(children)
            generate(children, indent_levels)