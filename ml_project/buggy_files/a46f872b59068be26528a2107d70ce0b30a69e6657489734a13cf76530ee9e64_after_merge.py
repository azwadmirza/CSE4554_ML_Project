    def json(self):
        """Custom JSON encoder"""
        attributes = {
            'type': self.type,
            'filename': self.filename,
            'line_number': self.lineno,
            'hashed_secret': self.secret_hash,
        }

        if self.is_secret is not None:
            attributes['is_secret'] = self.is_secret

        return attributes