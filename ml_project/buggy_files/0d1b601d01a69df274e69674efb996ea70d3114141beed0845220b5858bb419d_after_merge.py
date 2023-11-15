    def handle(self, *args, **options):
        # Optimize index
        if options['optimize']:
            optimize_fulltext()
            return
        fulltext = Fulltext()
        # Optionally rebuild indices from scratch
        if options['clean']:
            fulltext.cleanup()

        if options['all']:
            self.process_all(fulltext)
        else:
            self.process_filtered(fulltext, **options)