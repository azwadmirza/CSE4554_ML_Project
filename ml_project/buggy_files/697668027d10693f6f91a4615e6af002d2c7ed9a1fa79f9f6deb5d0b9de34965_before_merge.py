    def to_dict(self):
        return {
            'name': self.name,
            'trakt_id': self.id,
            'imdb_id': self.imdb,
            'tmdb_id': self.tmdb,
            'images': list_images(self.images)
        }