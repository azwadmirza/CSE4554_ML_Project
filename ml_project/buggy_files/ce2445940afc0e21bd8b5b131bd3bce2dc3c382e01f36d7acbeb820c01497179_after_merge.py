    def create_archive(self, body, description):
        archive_id = hashlib.md5(body).hexdigest()
        self.archives[archive_id] = {}
        self.archives[archive_id]["body"] = body
        self.archives[archive_id]["size"] = len(body)
        self.archives[archive_id]["sha256"] = hashlib.sha256(body).hexdigest()
        self.archives[archive_id]["creation_date"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.000Z")
        self.archives[archive_id]["description"] = description
        return archive_id