    def write_mo(self, locale):
        with open(self.po_path, 'rt') as po:
            with open(self.mo_path, 'wb') as mo:
                write_mo(mo, read_po(po, locale))