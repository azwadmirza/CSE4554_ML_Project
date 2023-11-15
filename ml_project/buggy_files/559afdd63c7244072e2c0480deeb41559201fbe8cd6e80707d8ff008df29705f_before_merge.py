        def append_fignumber(figtype, figure_id):
            if figure_id in self.builder.fignumbers.get(figtype, {}):
                prefix = self.builder.config.numfig_prefix.get(figtype, '')
                numbers = self.builder.fignumbers[figtype][figure_id]
                self.body.append(prefix + '.'.join(map(str, numbers)) + " ")