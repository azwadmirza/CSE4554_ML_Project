    def parse(self, report):
        raw_report = utils.base64_decode(report["raw"])
        # Temporary fix for https://github.com/certtools/intelmq/issues/967
        raw_report = raw_report.translate({0: None})
        csvr = csv.DictReader(io.StringIO(raw_report))

        # create an array of fieldnames,
        # those were automagically created by the dictreader
        self.fieldnames = csvr.fieldnames

        for row in csvr:
            yield row