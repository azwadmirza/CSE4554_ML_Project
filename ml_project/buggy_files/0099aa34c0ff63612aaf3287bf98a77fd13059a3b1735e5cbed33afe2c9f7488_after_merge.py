    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'version': [
                {'id': self.id,
                 'event_id': self.event_id,
                 'event_ver': self.event_ver,
                 'session_ver': self.session_ver,
                 'speakers_ver': self.speakers_ver,
                 'tracks_ver': self.tracks_ver,
                 'sponsors_ver': self.sponsors_ver,
                 'microlocations_ver': self.microlocations_ver}
            ]
        }