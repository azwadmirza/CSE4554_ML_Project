    def to_json(self):
        # type: () -> Dict[str, Union[str, int, bool]]
        json_submission = {
            'source_url': url_for('api.single_source',
                                  source_uuid=self.source.uuid),
            'reply_url': url_for('api.single_reply',
                                 source_uuid=self.source.uuid,
                                 reply_uuid=self.uuid),
            'filename': self.filename,
            'size': self.size,
            'journalist_username': self.journalist.username,
            'journalist_first_name': self.journalist.first_name,
            'journalist_last_name': self.journalist.last_name,
            'journalist_uuid': self.journalist.uuid,
            'uuid': self.uuid,
            'is_deleted_by_source': self.deleted_by_source,
        }
        return json_submission