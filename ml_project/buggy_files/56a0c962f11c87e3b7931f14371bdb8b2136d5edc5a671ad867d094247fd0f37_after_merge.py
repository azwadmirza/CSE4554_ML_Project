    def create_storage(self, name, **options):
        if name == "bigquery":
            return BigqueryStorage(**options)