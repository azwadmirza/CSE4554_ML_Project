    def run(self):  # pragma: no cover
        if self.o.rfile and not self.o.keepserving:
            self.shutdown()
            return
        try:
            return super(DumpMaster, self).run()
        except BaseException:
            self.shutdown()
            raise