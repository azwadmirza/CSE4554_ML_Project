    def handle(self, *args, **options):
        exts_pool.load_all()
        self.csvwriter = csv.writer(
            self.stdout, delimiter=smart_text(options["sepchar"]))
        getattr(self, "export_{}".format(options["objtype"]))()