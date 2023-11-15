    def _get_mime_headers(self):
        headers = []
        headers.append(('Project-Id-Version',
                        '%s %s' % (self.project, self.version)))
        headers.append(('Report-Msgid-Bugs-To', self.msgid_bugs_address))
        headers.append(('POT-Creation-Date',
                        format_datetime(self.creation_date, 'yyyy-MM-dd HH:mmZ',
                                        locale='en')))
        if isinstance(self.revision_date, (datetime, time_) + number_types):
            headers.append(('PO-Revision-Date',
                            format_datetime(self.revision_date,
                                            'yyyy-MM-dd HH:mmZ', locale='en')))
        else:
            headers.append(('PO-Revision-Date', self.revision_date))
        headers.append(('Last-Translator', self.last_translator))
        if self.locale is not None:
            headers.append(('Language', str(self.locale)))
        if (self.locale is not None) and ('LANGUAGE' in self.language_team):
            headers.append(('Language-Team',
                            self.language_team.replace('LANGUAGE',
                                                       str(self.locale))))
        else:
            headers.append(('Language-Team', self.language_team))
        if self.locale is not None:
            headers.append(('Plural-Forms', self.plural_forms))
        headers.append(('MIME-Version', '1.0'))
        headers.append(('Content-Type',
                        'text/plain; charset=%s' % self.charset))
        headers.append(('Content-Transfer-Encoding', '8bit'))
        headers.append(('Generated-By', 'Babel %s\n' % VERSION))
        return headers