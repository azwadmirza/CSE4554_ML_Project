    def _parse_date(self, date_text):
        return datetime.strptime(date_text, '%d-%m-%Y').date()