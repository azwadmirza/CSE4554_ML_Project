def searx_bang(full_query):
    '''check if the searchQuery contain a bang, and create fitting autocompleter results'''
    # check if there is a query which can be parsed
    if len(full_query.getSearchQuery()) == 0:
        return []

    results = []

    # check if current query stats with !bang
    first_char = full_query.getSearchQuery()[0]
    if first_char == '!' or first_char == '?':
        if len(full_query.getSearchQuery()) == 1:
            # show some example queries
            # TODO, check if engine is not avaliable
            results.append(first_char + "images")
            results.append(first_char + "wikipedia")
            results.append(first_char + "osm")
        else:
            engine_query = full_query.getSearchQuery()[1:]

            # check if query starts with categorie name
            for categorie in categories:
                if categorie.startswith(engine_query):
                    results.append(first_char + '{categorie}'.format(categorie=categorie))

            # check if query starts with engine name
            for engine in engines:
                if engine.startswith(engine_query.replace('_', ' ')):
                    results.append(first_char + '{engine}'.format(engine=engine.replace(' ', '_')))

            # check if query starts with engine shortcut
            for engine_shortcut in engine_shortcuts:
                if engine_shortcut.startswith(engine_query):
                    results.append(first_char + '{engine_shortcut}'.format(engine_shortcut=engine_shortcut))

    # check if current query stats with :bang
    elif first_char == ':':
        if len(full_query.getSearchQuery()) == 1:
            # show some example queries
            results.append(":en")
            results.append(":en_us")
            results.append(":english")
            results.append(":united_kingdom")
        else:
            engine_query = full_query.getSearchQuery()[1:]

            for lc in language_codes:
                lang_id, lang_name, country, english_name = map(unicode.lower, lc)

                # check if query starts with language-id
                if lang_id.startswith(engine_query):
                    if len(engine_query) <= 2:
                        results.append(u':{lang_id}'.format(lang_id=lang_id.split('-')[0]))
                    else:
                        results.append(u':{lang_id}'.format(lang_id=lang_id))

                # check if query starts with language name
                if lang_name.startswith(engine_query) or english_name.startswith(engine_query):
                    results.append(u':{lang_name}'.format(lang_name=lang_name))

                # check if query starts with country
                if country.startswith(engine_query.replace('_', ' ')):
                    results.append(u':{country}'.format(country=country.replace(' ', '_')))

    # remove duplicates
    result_set = set(results)

    # remove results which are already contained in the query
    for query_part in full_query.query_parts:
        if query_part in result_set:
            result_set.remove(query_part)

    # convert result_set back to list
    return list(result_set)