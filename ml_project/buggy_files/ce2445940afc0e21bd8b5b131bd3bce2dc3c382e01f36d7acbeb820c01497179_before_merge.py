    def create_archive(self, body):
        archive_id = hashlib.sha256(body).hexdigest()
        self.archives[archive_id] = body
        return archive_id