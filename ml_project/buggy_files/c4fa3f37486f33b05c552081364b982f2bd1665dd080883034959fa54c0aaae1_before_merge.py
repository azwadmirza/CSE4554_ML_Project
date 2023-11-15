    def getTrendingShowImage(indexerId):
        image_url = sickchill.indexer.series_poster_by_id(indexerId)
        if image_url:
            image_path = trakt_trending.get_image_path(trakt_trending.get_image_name(indexerId))
            trakt_trending.cache_image(image_url, image_path)
            return indexerId