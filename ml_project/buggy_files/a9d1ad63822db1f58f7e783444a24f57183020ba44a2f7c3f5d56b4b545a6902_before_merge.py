def save_cover(url, book_path):
    img = requests.get(url)
    if img.headers.get('content-type') != 'image/jpeg':
        web.app.logger.error("Cover is no jpg file, can't save")
        return False

    if ub.config.config_use_google_drive:
        tmpDir = gettempdir()
        f = open(os.path.join(tmpDir, "uploaded_cover.jpg"), "wb")
        f.write(img.content)
        f.close()
        uploadFileToEbooksFolder(os.path.join(book_path, 'cover.jpg'), os.path.join(tmpDir, f.name))
        web.app.logger.info("Cover is saved on Google Drive")
        return True

    f = open(os.path.join(ub.config.config_calibre_dir, book_path, "cover.jpg"), "wb")
    f.write(img.content)
    f.close()
    web.app.logger.info("Cover is saved")
    return True