    def run(self):
        # type: () -> List[nodes.Node]
        latex = '\n'.join(self.content)
        if self.arguments and self.arguments[0]:
            latex = self.arguments[0] + '\n\n' + latex
        node = nodes.math_block(latex, latex,
                                docname=self.state.document.settings.env.docname,
                                number=self.options.get('name'),
                                label=self.options.get('label'),
                                nowrap='nowrap' in self.options)
        ret = [node]
        set_source_info(self, node)
        self.add_target(ret)
        return ret