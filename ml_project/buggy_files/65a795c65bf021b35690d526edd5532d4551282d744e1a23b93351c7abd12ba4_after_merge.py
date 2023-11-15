    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "year": self.year,
            "slug": self.slug,
            "imdb_id": self.imdb_id,
            "tmdb_id": self.tmdb_id,
            "tagline": self.tagline,
            "overview": self.overview,
            "released": self.released,
            "runtime": self.runtime,
            "rating": self.rating,
            "votes": self.votes,
            "language": self.language,
            "homepage": self.homepage,
            "trailer": self.trailer,
            "genres": [g.name for g in self.genres],
            "updated_at": self.updated_at,
            "cached_at": self.cached_at,
            "main_image": self.main_image,
            "images": {
                'fanart': {
                    'full': self.image_fanart_full,
                    'medium': self.image_fanart_medium,
                    'thumb': self.image_fanart_thumb
                },
                'poster': {
                    'full': self.image_poster_full,
                    'medium': self.image_poster_medium,
                    'thumb': self.image_poster_thumb
                },
                'logo': {
                    'full': self.image_logo_full
                },
                'clearart': {
                    'full': self.image_clearart_full
                },
                'banner': {
                    'full': self.image_banner_full
                },
                'thumb': {
                    'full': self.image_thumb_full
                }
            }
        }