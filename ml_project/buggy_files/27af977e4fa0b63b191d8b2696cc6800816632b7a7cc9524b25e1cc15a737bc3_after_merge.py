    def run(self):
        """ Search for a show with a given name on all the indexers, in a specific language """

        results = []
        lang_id = self.valid_languages[self.lang]

        if self.name and not self.indexerid:  # only name was given
            search_results = sickchill.indexer.search_indexers_for_series_name(self.name, self.lang)
            for indexer, indexer_results in search_results.items():
                for result in indexer_results:
                    # Skip it if it's in our show list already, and we only want new shows
                    in_show_list = sickchill.show.Show.Show.find(settings.showList, int(result['id'])) is not None
                    if in_show_list and self.only_new:
                        continue

                    results.append({
                        indexer_ids[indexer]: result['id'],
                        "name": result['seriesName'],
                        "first_aired": result['firstAired'],
                        "indexer": indexer,
                        "in_show_list": in_show_list
                    })

                return _responds(RESULT_SUCCESS, {"results": results, "langid": lang_id})

        elif self.indexerid:
            indexer, result = sickchill.indexer.search_indexers_for_series_id(indexerid=self.indexerid, language=self.lang)
            if not indexer:
                logger.warning("API :: Unable to find show with id " + str(self.indexerid))
                return _responds(RESULT_SUCCESS, {"results": [], "langid": lang_id})

            if not result.seriesName:
                logger.debug(
                    "API :: Found show with indexerid: " + str(self.indexerid) + ", however it contained no show name")
                return _responds(RESULT_FAILURE, msg="Show contains no name, invalid result")

            results = [{
                indexer_ids[indexer]: result.id,
                "name": str(result.seriesName),
                "first_aired": result.firstAired,
                "indexer": indexer
            }]

            return _responds(RESULT_SUCCESS, {"results": results, "langid": lang_id})
        else:
            return _responds(RESULT_FAILURE, msg="Either a unique id or name is required!")