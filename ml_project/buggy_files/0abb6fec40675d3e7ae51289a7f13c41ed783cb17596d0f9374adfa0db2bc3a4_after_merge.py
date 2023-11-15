def read_book(book_id, book_format):
    book = db.session.query(db.Books).filter(db.Books.id == book_id).first()
    if not book:
        flash(_(u"Error opening eBook. File does not exist or file is not accessible:"), category="error")
        return redirect(url_for("index"))

    # check if book has bookmark
    lbookmark = None
    if current_user.is_authenticated:
        lbookmark = ub.session.query(ub.Bookmark).filter(ub.and_(ub.Bookmark.user_id == int(current_user.id),
                                                            ub.Bookmark.book_id == book_id,
                                                            ub.Bookmark.format == book_format.upper())).first()
    if book_format.lower() == "epub":
        return render_title_template('read.html', bookid=book_id, title=_(u"Read a Book"), bookmark=lbookmark)
    elif book_format.lower() == "pdf":
        return render_title_template('readpdf.html', pdffile=book_id, title=_(u"Read a Book"))
    elif book_format.lower() == "txt":
        return render_title_template('readtxt.html', txtfile=book_id, title=_(u"Read a Book"))
    else:
        book_dir = os.path.join(config.get_main_dir, "cps", "static", str(book_id))
        if not os.path.exists(book_dir):
            os.mkdir(book_dir)
        for fileext in ["cbr", "cbt", "cbz"]:
            if book_format.lower() == fileext:
                all_name = str(book_id) # + "/" + book.data[0].name + "." + fileext
                #tmp_file = os.path.join(book_dir, book.data[0].name) + "." + fileext
                #if not os.path.exists(all_name):
                #    cbr_file = os.path.join(config.config_calibre_dir, book.path, book.data[0].name) + "." + fileext
                #    copyfile(cbr_file, tmp_file)
                return render_title_template('readcbr.html', comicfile=all_name, title=_(u"Read a Book"),
                                             extension=fileext)
        '''if rar_support == True:
            extensionList = ["cbr","cbt","cbz"]
        else:
            extensionList = ["cbt","cbz"]
        for fileext in extensionList:
            if book_format.lower() == fileext:
                return render_title_template('readcbr.html', comicfile=book_id, 
                extension=fileext, title=_(u"Read a Book"), book=book)
        flash(_(u"Error opening eBook. File does not exist or file is not accessible."), category="error")
        return redirect(url_for("index"))'''
        flash(_(u"Error opening eBook. Fileformat is not supported."), category="error")
        return redirect(url_for("index"))