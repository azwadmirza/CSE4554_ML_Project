    def process(self):
        report = self.receive_message()

        if report is None or not report.contains("raw"):
            self.acknowledge_message()
            return

        raw_report = utils.base64_decode(report.value("raw"))

        fp = io.StringIO(raw_report)
        rows = csv.DictReader(fp)

        for row in rows:
            event = Event(report)

            for key, value in row.items():
                if not value:
                    continue

                if key is None:
                    self.logger.warning('Value without key found, skipping the'
                                        ' value: {!r}'.format(value))
                    continue

                key = COLUMNS[key]

                if key == "__IGNORE__" or key == "__TDB__":
                    continue

                if key == "source.fqdn" and IPAddress.is_valid(value,
                                                               sanitize=True):
                    continue

                if key == "time.source":
                    value = value + " UTC"

                event.add(key, value, sanitize=True)

            event.add('classification.type', u'phishing')
            event.add("raw", ",".join(row), sanitize=True)

            self.send_message(event)
        self.acknowledge_message()