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
            "images": list_images(self.images)
        }