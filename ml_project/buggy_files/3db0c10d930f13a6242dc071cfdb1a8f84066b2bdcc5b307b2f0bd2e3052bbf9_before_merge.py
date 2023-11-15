    def parse(self, report):
        report_split = utils.base64_decode(report["raw"]).strip().splitlines()
        self.tempdata = report_split[:2]
        for line in report_split[3:]:
            yield line.strip()