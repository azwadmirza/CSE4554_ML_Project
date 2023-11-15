    def handle(self, *args, **options):
        fulltext = Fulltext()
        # Optimize index
        if options['optimize']:
            self.optimize_index(fulltext)
            return
        # Optionally rebuild indices from scratch
        if options['clean']:
            fulltext.cleanup()

        if options['all']:
            self.process_all(fulltext)
        else:
            self.process_filtered(fulltext, **options)