    def to_json(self):
        # type: () -> Dict[str, Union[str, int, bool]]
        username = "deleted"
        first_name = ""
        last_name = ""
        uuid = "deleted"
        if self.journalist:
            username = self.journalist.username
            first_name = self.journalist.first_name
            last_name = self.journalist.last_name
            uuid = self.journalist.uuid
        json_submission = {
            'source_url': url_for('api.single_source',
                                  source_uuid=self.source.uuid),
            'reply_url': url_for('api.single_reply',
                                 source_uuid=self.source.uuid,
                                 reply_uuid=self.uuid),
            'filename': self.filename,
            'size': self.size,
            'journalist_username': username,
            'journalist_first_name': first_name,
            'journalist_last_name': last_name,
            'journalist_uuid': uuid,
            'uuid': self.uuid,
            'is_deleted_by_source': self.deleted_by_source,
        }
        return json_submission