    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "year": self.year,
            "slug": self.slug,
            "tvdb_id": self.tvdb_id,
            "imdb_id": self.imdb_id,
            "tmdb_id": self.tmdb_id,
            "tvrage_id": self.tvrage_id,
            "overview": self.overview,
            "first_aired": self.first_aired,
            "air_day": self.air_day,
            "air_time": self.air_time.strftime("%H:%M") if self.air_time else None,
            "timezone": self.timezone,
            "runtime": self.runtime,
            "certification": self.certification,
            "network": self.network,
            "country": self.country,
            "status": self.status,
            "rating": self.rating,
            "votes": self.votes,
            "language": self.language,
            "homepage": self.homepage,
            "number_of_aired_episodes": self.aired_episodes,
            "genres": [g.name for g in self.genres],
            "updated_at": self.updated_at,
            "cached_at": self.cached_at,
            "images": {
                'poster': {
                    'full': self.image_poster_full,
                    'medium': self.image_poster_medium,
                    'thumb': self.image_poster_thumb
                },
                'thumb': {
                    'full': self.image_thumb_full
                }
            },
            "main_image": self.main_image
        }