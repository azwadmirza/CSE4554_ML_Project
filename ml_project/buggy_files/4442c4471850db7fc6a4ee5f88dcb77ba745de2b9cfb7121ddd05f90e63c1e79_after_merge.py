def update_dir_structure_file(book_id, calibrepath, first_author):
    localbook = db.session.query(db.Books).filter(db.Books.id == book_id).first()
    path = os.path.join(calibrepath, localbook.path)

    authordir = localbook.path.split('/')[0]
    if first_author:
        new_authordir = get_valid_filename(first_author)
    else:
        new_authordir = get_valid_filename(localbook.authors[0].name)

    titledir = localbook.path.split('/')[1]
    new_titledir = get_valid_filename(localbook.title) + " (" + str(book_id) + ")"

    if titledir != new_titledir:
        try:
            new_title_path = os.path.join(os.path.dirname(path), new_titledir)
            if not os.path.exists(new_title_path):
                os.renames(path, new_title_path)
            else:
                web.app.logger.info("Copying title: " + path + " into existing: " + new_title_path)
                for dir_name, subdir_list, file_list in os.walk(path):
                    for file in file_list:
                        os.renames(os.path.join(dir_name, file),
                                   os.path.join(new_title_path + dir_name[len(path):], file))
            path = new_title_path
            localbook.path = localbook.path.split('/')[0] + '/' + new_titledir
        except OSError as ex:
            web.app.logger.error("Rename title from: " + path + " to " + new_title_path + ": " + str(ex))
            web.app.logger.debug(ex, exc_info=True)
            return _("Rename title from: '%(src)s' to '%(dest)s' failed with error: %(error)s",
                     src=path, dest=new_title_path, error=str(ex))
    if authordir != new_authordir:
        try:
            new_author_path = os.path.join(calibrepath, new_authordir, os.path.basename(path))
            os.renames(path, new_author_path)
            localbook.path = new_authordir + '/' + localbook.path.split('/')[1]
        except OSError as ex:
            web.app.logger.error("Rename author from: " + path + " to " + new_author_path + ": " + str(ex))
            web.app.logger.debug(ex, exc_info=True)
            return _("Rename author from: '%(src)s' to '%(dest)s' failed with error: %(error)s",
                     src=path, dest=new_author_path, error=str(ex))
    # Rename all files from old names to new names
    if authordir != new_authordir or titledir != new_titledir:
        try:
            new_name = get_valid_filename(localbook.title) + ' - ' + get_valid_filename(new_authordir)
            path_name = os.path.join(calibrepath, new_authordir, os.path.basename(path))
            for file_format in localbook.data:
                os.renames(os.path.join(path_name, file_format.name + '.' + file_format.format.lower()),
                           os.path.join(path_name, new_name + '.' + file_format.format.lower()))
                file_format.name = new_name
        except OSError as ex:
            web.app.logger.error("Rename file in path " + path + " to " + new_name + ": " + str(ex))
            web.app.logger.debug(ex, exc_info=True)
            return _("Rename file in path '%(src)s' to '%(dest)s' failed with error: %(error)s",
                     src=path, dest=new_name, error=str(ex))
    return False