    def load_rules_from_string(self, stringvalue):
        for line in stringvalue.splitlines():
            stringline = line.rstrip()
            if line.startswith('#') and not line.isspace():
                self.preamble.append(line.rstrip())
            elif (not line.startswith('#') and
                  not line.isspace() and
                  len(line) != 0):
                try:
                    self.ansible.log(msg="Creating rule from string %s" % stringline)
                except AttributeError:
                    pass
                self.rules.append(PamdRule.rulefromstring(stringline))