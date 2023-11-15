    def _mixin_after_parsed(self):
        if not self.args:
            self.print_help()
            self.exit(1)

        if self.options.list:
            if ',' in self.args[0]:
                self.config['tgt'] = self.args[0].split(',')
            else:
                self.config['tgt'] = self.args[0].split()
        else:
            self.config['tgt'] = self.args[0]
        if len(self.args) > 0:
            self.config['arg_str'] = ' '.join(self.args[1:])