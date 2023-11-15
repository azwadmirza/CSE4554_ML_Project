    def process_message(self, uid, message):
        seen = False

        for attach in message.attachments:
            if not attach:
                continue

            attach_filename = attach['filename']
            if attach_filename.startswith('"'):  # for imbox versions older than 0.9.5, see also above
                attach_filename = attach_filename[1:-1]

            if re.search(self.parameters.attach_regex, attach_filename):

                self.logger.debug("Found suitable attachment %s.", attach_filename)

                report = self.new_report()

                if self.extract_files:
                    raw_reports = unzip(attach['content'].read(), self.extract_files,
                                        return_names=True, logger=self.logger)
                else:
                    raw_reports = ((None, attach['content'].read()), )

                for file_name, raw_report in raw_reports:
                    report = self.new_report()
                    report.add("raw", raw_report)
                    if file_name:
                        report.add("extra.file_name", file_name)
                    report["extra.email_subject"] = message.subject
                    report["extra.email_from"] = ','.join(x['email'] for x in message.sent_from)
                    report["extra.email_message_id"] = message.message_id
                    self.send_message(report)

                # Only mark read if message relevant to this instance,
                # so other instances watching this mailbox will still
                # check it.
                seen = True
        self.logger.info("Email report read.")
        return seen