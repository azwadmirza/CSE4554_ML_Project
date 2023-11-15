    def to_taskwarrior(self):
        return {
            'project': self.extra['project'],
            'annotations': self.extra['annotations'],
            self.URL: self.extra['url'],

            'priority': self.origin['default_priority'],
            'tags': self.get_tags(),
            self.FOREIGN_ID: self.record['ref'],
            self.SUMMARY: self.record['subject'],
        }