        def append_fignumber(figtype, figure_id):
            if figure_id in self.builder.fignumbers.get(figtype, {}):
                self.body.append(self.starttag(node, 'span', '', CLASS='caption-number'))
                prefix = self.builder.config.numfig_prefix.get(figtype, '')
                numbers = self.builder.fignumbers[figtype][figure_id]
                self.body.append(prefix + '.'.join(map(str, numbers)) + " ")
                self.body.append('</span>')