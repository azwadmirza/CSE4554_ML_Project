def language_overview():
    if current_user.show_language():
        if current_user.filter_language() == u"all":
            languages = speaking_language()
        else:
            try:
                cur_l = LC.parse(current_user.filter_language())
            except UnknownLocaleError:
                cur_l = None
            languages = db.session.query(db.Languages).filter(
                db.Languages.lang_code == current_user.filter_language()).all()
            if cur_l:
                languages[0].name = cur_l.get_language_name(get_locale())
            else:
                languages[0].name = _(isoLanguages.get(part3=languages[0].lang_code).name)
        lang_counter = db.session.query(db.books_languages_link,
                                        func.count('books_languages_link.book').label('bookcount')).group_by(
            text('books_languages_link.lang_code')).all()
        return render_title_template('languages.html', languages=languages, lang_counter=lang_counter,
                                     title=_(u"Available languages"), page="langlist")
    else:
        abort(404)