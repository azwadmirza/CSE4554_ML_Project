    def parse(self, report):
        raw_report = utils.base64_decode(report.get("raw"))
        # ignore lines starting with #
        raw_report = re.sub(r'(?m)^#.*\n?', '', raw_report)
        # ignore null bytes
        raw_report = re.sub(r'(?m)\0', '', raw_report)
        # skip header
        if getattr(self.parameters, 'skip_header', False):
            raw_report = raw_report[raw_report.find('\n') + 1:]
        for row in csv.reader(io.StringIO(raw_report),
                              delimiter=str(self.parameters.delimiter)):

            if self.filter_text and self.filter_type:
                text_in_row = self.filter_text in self.parameters.delimiter.join(row)
                if text_in_row and self.filter_type == 'whitelist':
                    yield row
                elif not text_in_row and self.filter_type == 'blacklist':
                    yield row
                else:
                    continue
            else:
                    yield row