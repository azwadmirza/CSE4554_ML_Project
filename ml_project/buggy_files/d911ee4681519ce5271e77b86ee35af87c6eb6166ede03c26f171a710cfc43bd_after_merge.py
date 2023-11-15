    def write_mo(self, locale, warnfunc):
        with io.open(self.po_path, 'rt', encoding=self.charset) as file_po:
            try:
                po = read_po(file_po, locale)
            except Exception:
                warnfunc('reading error: %s' % self.po_path)
                return

        with io.open(self.mo_path, 'wb') as file_mo:
            try:
                write_mo(file_mo, po)
            except Exception:
                warnfunc('writing error: %s' % self.mo_path)