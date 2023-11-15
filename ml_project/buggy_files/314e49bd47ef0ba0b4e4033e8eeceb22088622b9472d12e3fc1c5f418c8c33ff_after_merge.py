    def write_mo(self, locale):
        with io.open(self.po_path, 'rt', encoding=self.charset) as po:
            with io.open(self.mo_path, 'wb') as mo:
                write_mo(mo, read_po(po, locale))