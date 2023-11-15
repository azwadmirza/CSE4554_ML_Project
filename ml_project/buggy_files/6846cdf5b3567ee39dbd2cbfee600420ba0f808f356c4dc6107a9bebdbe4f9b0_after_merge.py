    def name(self):
        res = self.get_value('package/name')
        if not res:
            sys.exit('Error: package/name missing in: %r' % self.meta_path)
        res = str(res)
        if res != res.lower():
            sys.exit('Error: package/name must be lowercase, got: %r' % res)
        return res