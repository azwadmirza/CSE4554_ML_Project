    def recover_line(self, line):
        out = self.header + '\n'
        ordered_line = [self.conv_csv_shadowserver(line[v]) for v in
                        self.fieldnames]
        out += ','.join(ordered_line) + '\n'
        return out