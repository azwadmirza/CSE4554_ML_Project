    def _get_header_comment(self):
        comment = self._header_comment
        year = datetime.now(LOCALTZ).strftime('%Y')
        if hasattr(self.revision_date, 'strftime'):
            year = self.revision_date.strftime('%Y')
        comment = comment.replace('PROJECT', self.project) \
                         .replace('VERSION', self.version) \
                         .replace('YEAR', year) \
                         .replace('ORGANIZATION', self.copyright_holder)
        locale_name = (self.locale.english_name if self.locale else self.locale_identifier)
        if locale_name:
            comment = comment.replace('Translations template', '%s translations' % locale_name)
        return comment