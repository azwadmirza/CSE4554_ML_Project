    def handle(self, *args, **options):
        exts_pool.load_all()
        self.csvwriter = csv.writer(sys.stdout, delimiter=options["sepchar"])
        getattr(self, "export_{}".format(options["objtype"]))()