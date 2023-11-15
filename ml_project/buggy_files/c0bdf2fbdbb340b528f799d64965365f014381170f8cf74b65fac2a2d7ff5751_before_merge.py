def advanced_search():
    # Build custom columns names
    tmpcc = db.session.query(db.Custom_Columns).filter(db.Custom_Columns.datatype.notin_(db.cc_exceptions)).all()
    if config.config_columns_to_ignore:
        cc = []
        for col in tmpcc:
            r = re.compile(config.config_columns_to_ignore)
            if r.match(col.label):
                cc.append(col)
    else:
        cc = tmpcc

    db.session.connection().connection.connection.create_function("lower", 1, db.lcase)
    q = db.session.query(db.Books)
    # postargs = request.form.to_dict()

    include_tag_inputs = request.args.getlist('include_tag')
    exclude_tag_inputs = request.args.getlist('exclude_tag')
    include_series_inputs = request.args.getlist('include_serie')
    exclude_series_inputs = request.args.getlist('exclude_serie')
    include_languages_inputs = request.args.getlist('include_language')
    exclude_languages_inputs = request.args.getlist('exclude_language')

    author_name = request.args.get("author_name")
    book_title = request.args.get("book_title")
    publisher = request.args.get("publisher")
    pub_start = request.args.get("Publishstart")
    pub_end = request.args.get("Publishend")
    rating_low = request.args.get("ratinghigh")
    rating_high = request.args.get("ratinglow")
    description = request.args.get("comment")
    if author_name: author_name = author_name.strip().lower().replace(',','|')
    if book_title: book_title = book_title.strip().lower()
    if publisher: publisher = publisher.strip().lower()

    searchterm = []
    cc_present = False
    for c in cc:
        if request.args.get('custom_column_' + str(c.id)):
            searchterm.extend([(u"%s: %s" % (c.name, request.args.get('custom_column_' + str(c.id))))])
            cc_present = True

    if include_tag_inputs or exclude_tag_inputs or include_series_inputs or exclude_series_inputs or \
            include_languages_inputs or exclude_languages_inputs or author_name or book_title or \
            publisher or pub_start or pub_end or rating_low or rating_high or description or cc_present:
        searchterm = []
        searchterm.extend((author_name.replace('|',','), book_title, publisher))
        if pub_start:
            try:
                searchterm.extend([_(u"Published after ") +
                               format_date(datetime.datetime.strptime(pub_start,"%Y-%m-%d"),
                                           format='medium', locale=get_locale())])
            except ValueError:
                pub_start = u""
        if pub_end:
            try:
                searchterm.extend([_(u"Published before ") +
                               format_date(datetime.datetime.strptime(pub_end,"%Y-%m-%d"),
                                           format='medium', locale=get_locale())])
            except ValueError:
                pub_start = u""
        tag_names = db.session.query(db.Tags).filter(db.Tags.id.in_(include_tag_inputs)).all()
        searchterm.extend(tag.name for tag in tag_names)
        serie_names = db.session.query(db.Series).filter(db.Series.id.in_(include_series_inputs)).all()
        searchterm.extend(serie.name for serie in serie_names)
        language_names = db.session.query(db.Languages).filter(db.Languages.id.in_(include_languages_inputs)).all()
        if language_names:
            language_names = speaking_language(language_names)
        searchterm.extend(language.name for language in language_names)
        if rating_high:
            searchterm.extend([_(u"Rating <= %(rating)s", rating=rating_high)])
        if rating_low:
            searchterm.extend([_(u"Rating >= %(rating)s", rating=rating_low)])
        # handle custom columns
        for c in cc:
            if request.args.get('custom_column_' + str(c.id)):
                searchterm.extend([(u"%s: %s" % (c.name, request.args.get('custom_column_' + str(c.id))))])
        searchterm = " + ".join(filter(None, searchterm))
        q = q.filter()
        if author_name:
            q = q.filter(db.Books.authors.any(db.Authors.name.ilike("%" + author_name + "%")))
        if book_title:
            q = q.filter(db.Books.title.ilike("%" + book_title + "%"))
        if pub_start:
            q = q.filter(db.Books.pubdate >= pub_start)
        if pub_end:
            q = q.filter(db.Books.pubdate <= pub_end)
        if publisher:
            q = q.filter(db.Books.publishers.any(db.Publishers.name.ilike("%" + publisher + "%")))
        for tag in include_tag_inputs:
            q = q.filter(db.Books.tags.any(db.Tags.id == tag))
        for tag in exclude_tag_inputs:
            q = q.filter(not_(db.Books.tags.any(db.Tags.id == tag)))
        for serie in include_series_inputs:
            q = q.filter(db.Books.series.any(db.Series.id == serie))
        for serie in exclude_series_inputs:
            q = q.filter(not_(db.Books.series.any(db.Series.id == serie)))
        if current_user.filter_language() != "all":
            q = q.filter(db.Books.languages.any(db.Languages.lang_code == current_user.filter_language()))
        else:
            for language in include_languages_inputs:
                q = q.filter(db.Books.languages.any(db.Languages.id == language))
            for language in exclude_languages_inputs:
                q = q.filter(not_(db.Books.series.any(db.Languages.id == language)))
        if rating_high:
            q = q.filter(db.Books.ratings.any(db.Ratings.id <= rating_high))
        if rating_low:
            q = q.filter(db.Books.ratings.any(db.Ratings.id >= rating_low))
        if description:
            q = q.filter(db.Books.comments.any(db.Comments.text.ilike("%" + description + "%")))

        # search custom culumns
        for c in cc:
            custom_query = request.args.get('custom_column_' + str(c.id))
            if custom_query:
                if c.datatype == 'bool':
                    getattr(db.Books, 'custom_column_1')
                    q = q.filter(getattr(db.Books, 'custom_column_'+str(c.id)).any(
                        db.cc_classes[c.id].value == (custom_query== "True") ))
                elif c.datatype == 'int':
                    q = q.filter(getattr(db.Books, 'custom_column_'+str(c.id)).any(
                        db.cc_classes[c.id].value == custom_query ))
                else:
                    q = q.filter(getattr(db.Books, 'custom_column_'+str(c.id)).any(
                        db.cc_classes[c.id].value.ilike("%" + custom_query + "%")))
        q = q.all()
        ids = list()
        for element in q:
            ids.append(element.id)
        ub.searched_ids[current_user.id] = ids
        return render_title_template('search.html', searchterm=searchterm,
                                     entries=q, title=_(u"search"), page="search")
    # prepare data for search-form
    tags = db.session.query(db.Tags).order_by(db.Tags.name).all()
    series = db.session.query(db.Series).order_by(db.Series.name).all()
    if current_user.filter_language() == u"all":
        languages = speaking_language()
    else:
        languages = None
    return render_title_template('search_form.html', tags=tags, languages=languages,
                                 series=series, title=_(u"search"), cc=cc, page="advsearch")