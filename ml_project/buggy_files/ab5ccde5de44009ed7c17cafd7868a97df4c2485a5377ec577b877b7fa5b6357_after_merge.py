def update_dir_structure_gdrive(book_id, first_author):
    error = False
    book = db.session.query(db.Books).filter(db.Books.id == book_id).first()
    path = book.path

    authordir = book.path.split('/')[0]
    if first_author:
        new_authordir = get_valid_filename(first_author)
    else:
        new_authordir = get_valid_filename(book.authors[0].name)
    titledir = book.path.split('/')[1]
    new_titledir = get_valid_filename(book.title) + u" (" + str(book_id) + u")"

    if titledir != new_titledir:
        gFile = gd.getFileFromEbooksFolder(os.path.dirname(book.path), titledir)
        if gFile:
            gFile['title'] = new_titledir
            gFile.Upload()
            book.path = book.path.split('/')[0] + u'/' + new_titledir
            path = book.path
            gd.updateDatabaseOnEdit(gFile['id'], book.path)     # only child folder affected
        else:
            error = _(u'File %(file)s not found on Google Drive', file=book.path) # file not found

    if authordir != new_authordir:
        gFile = gd.getFileFromEbooksFolder(os.path.dirname(book.path), new_titledir)
        if gFile:
            gd.moveGdriveFolderRemote(gFile, new_authordir)
            book.path = new_authordir + u'/' + book.path.split('/')[1]
            path = book.path
            gd.updateDatabaseOnEdit(gFile['id'], book.path)
        else:
            error = _(u'File %(file)s not found on Google Drive', file=authordir) # file not found
    # Rename all files from old names to new names

    if authordir != new_authordir or titledir != new_titledir:
        new_name = get_valid_filename(book.title) + u' - ' + get_valid_filename(new_authordir)
        for file_format in book.data:
            gFile = gd.getFileFromEbooksFolder(path, file_format.name + u'.' + file_format.format.lower())
            if not gFile:
                error = _(u'File %(file)s not found on Google Drive', file=file_format.name)  # file not found
                break
            gd.moveGdriveFileRemote(gFile, new_name + u'.' + file_format.format.lower())
            file_format.name = new_name
    return error