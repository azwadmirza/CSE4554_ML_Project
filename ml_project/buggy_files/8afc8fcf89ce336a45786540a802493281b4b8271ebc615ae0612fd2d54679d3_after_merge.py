    def _create_recommended_show(self, storage_key, series):
        """Create the RecommendedShow object from the returned showobj."""
        try:
            tvdb_id = cached_aid_to_tvdb(series.aid)
        except Exception:
            log.warning("Couldn't map AniDB id {0} to a TVDB id", series.aids)
            return None

        # If the anime can't be mapped to a tvdb_id, return none, and move on to the next.
        if not tvdb_id:
            return tvdb_id

        rec_show = RecommendedShow(
            self,
            series.aid,
            series.title,
            INDEXER_TVDBV2,
            tvdb_id,
            **{'rating': series.rating_permanent,
                'votes': series.count_permanent,
                'image_href': self.base_url.format(aid=series.aid),
                'ids': {'tvdb': tvdb_id,
                        'aid': series.aid
                        }
               }
        )

        # Check cache or get and save image
        use_default = self.default_img_src if not series.picture.url else None
        rec_show.cache_image(series.picture.url, default=use_default)

        # By default pre-configure the show option anime = True
        rec_show.is_anime = True

        return rec_show