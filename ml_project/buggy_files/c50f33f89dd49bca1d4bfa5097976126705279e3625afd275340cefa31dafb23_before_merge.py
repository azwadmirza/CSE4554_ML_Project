    def load_rules_from_file(self):
        self.fname = self.path + "/" + self.name
        stringline = ''
        try:
            for line in open(self.fname, 'r'):
                stringline += line.rstrip()
                stringline += '\n'
            self.load_rules_from_string(stringline)

        except IOError:
            e = get_exception()
            self.ansible.fail_json(msg='Unable to open/read PAM module \
                                   file %s with error %s.  And line %s' %
                                   (self.fname, str(e), stringline))