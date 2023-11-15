def save_cover(img, book_path):
    content_type = img.headers.get('content-type')
    if content_type not in ('image/jpeg', 'image/png', 'image/webp'):
        web.app.logger.error("Only jpg/jpeg/png/webp files are supported as coverfile")
        return False

    # convert to jpg because calibre only supports jpg
    if content_type in ('image/png', 'image/webp'):
        if hasattr(img,'stream'):
            imgc = Image.open(img.stream)
        else:
            imgc = Image.open(io.BytesIO(img.content))
        im = imgc.convert('RGB')
        tmp_bytesio = io.BytesIO()
        im.save(tmp_bytesio, format='JPEG')
        img._content = tmp_bytesio.getvalue()

    if ub.config.config_use_google_drive:
        tmpDir = gettempdir()
        if save_cover_from_filestorage(tmpDir, "uploaded_cover.jpg", img) is True:
            gd.uploadFileToEbooksFolder(os.path.join(book_path, 'cover.jpg'),
                                        os.path.join(tmpDir, "uploaded_cover.jpg"))
            web.app.logger.info("Cover is saved on Google Drive")
            return True
        else:
            return False
    else:
        return save_cover_from_filestorage(os.path.join(ub.config.config_calibre_dir, book_path), "cover.jpg", img)