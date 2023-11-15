def update_dir_stucture(book_id, calibrepath):
    if ub.config.config_use_google_drive:
        return update_dir_structure_gdrive(book_id)
    else:
        return update_dir_structure_file(book_id, calibrepath)