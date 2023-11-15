    def to_dict(self):
        return {
            'name': self.name,
            'trakt_id': self.id,
            'imdb_id': self.imdb,
            'tmdb_id': self.tmdb,
            'images': {
                'headshot': {
                    'full': self.image_headshot_full,
                    'medium': self.image_headshot_medium,
                    'thumb': self.image_headshot_thumb
                },
                'fanart': {
                    'full': self.image_fanart_full,
                    'medium': self.image_fanart_medium,
                    'thumb': self.image_fanart_thumb
                }
            },
            "main_image": self.main_image
        }