        def get_entries_query(cls, metadata_type=None, channel_pk=None,
                              exclude_deleted=False, hide_xxx=False, exclude_legacy=False, origin_id=None,
                              sort_by=None, sort_asc=True, query_filter=None, infohash=None):
            # Warning! For Pony magic to work, iteration variable name (e.g. 'g') should be the same everywhere!
            # Filter the results on a keyword or some keywords

            # FIXME: it is dangerous to mix query attributes. Should be handled by higher level methods instead
            # If we get a hex-encoded public key or infohash in the query_filter field, we drop the filter,
            # and instead query by public_key or infohash field. However, we only do this if there is no
            # channel_pk or origin_id attributes set, because we only want this special treatment of query_filter
            # argument for global search queries. In other words, named arguments have priority over hacky shenaningans
            if query_filter:
                normal_filter = query_filter.replace('"', '').replace("*", "")
                if is_hex_string(normal_filter) and len(normal_filter) % 2 == 0:
                    query_blob = database_blob(unhexlify(normal_filter))
                    if is_channel_public_key(normal_filter):
                        if (origin_id is None) and not channel_pk:
                            channel_pk = query_blob
                            query_filter = None
                    elif is_infohash(normal_filter):
                        infohash = query_blob
                        query_filter = None

            pony_query = cls.search_keyword(query_filter, lim=1000) if query_filter else select(g for g in cls)

            if isinstance(metadata_type, list):
                pony_query = pony_query.where(lambda g: g.metadata_type in metadata_type)
            else:
                pony_query = pony_query.where(
                    metadata_type=metadata_type if metadata_type is not None else cls._discriminator_)

            # Note that origin_id and channel_pk can be 0 and "" respectively, for, say, root channel and FFA entry
            pony_query = pony_query.where(public_key=(b"" if channel_pk == NULL_KEY_SUBST else channel_pk))\
                if channel_pk is not None else pony_query
            pony_query = pony_query.where(origin_id=origin_id) if origin_id is not None else pony_query
            pony_query = pony_query.where(lambda g: g.status != TODELETE) if exclude_deleted else pony_query
            pony_query = pony_query.where(lambda g: g.xxx == 0) if hide_xxx else pony_query
            pony_query = pony_query.where(lambda g: g.status != LEGACY_ENTRY) if exclude_legacy else pony_query
            pony_query = pony_query.where(lambda g: g.infohash == infohash) if infohash else pony_query

            # Sort the query
            if sort_by == "HEALTH":
                pony_query = pony_query.sort_by("(g.health.seeders, g.health.leechers)") if sort_asc else \
                    pony_query.sort_by("(desc(g.health.seeders), desc(g.health.leechers))")
            elif sort_by:
                sort_expression = "g." + sort_by
                sort_expression = sort_expression if sort_asc else desc(sort_expression)
                pony_query = pony_query.sort_by(sort_expression)

            return pony_query