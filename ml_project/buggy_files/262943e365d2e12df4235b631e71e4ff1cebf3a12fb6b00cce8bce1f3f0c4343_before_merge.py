    def to_json(self) -> 'Dict[str, Union[str, int, bool]]':
        json_submission = {
            'source_url': url_for('api.single_source',
                                  source_uuid=self.source.uuid),
            'submission_url': url_for('api.single_submission',
                                      source_uuid=self.source.uuid,
                                      submission_uuid=self.uuid),
            'filename': self.filename,
            'size': self.size,
            'is_read': self.downloaded,
            'uuid': self.uuid,
            'download_url': url_for('api.download_submission',
                                    source_uuid=self.source.uuid,
                                    submission_uuid=self.uuid),
        }
        return json_submission