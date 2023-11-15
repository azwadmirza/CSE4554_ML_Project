def extractCover(tmp_file_name, original_file_extension):
    cover_data = None
    if original_file_extension.upper() == '.CBZ':
        cf = zipfile.ZipFile(tmp_file_name)
        for name in cf.namelist():
            ext = os.path.splitext(name)
            if len(ext) > 1:
                extension = ext[1].lower()
                if extension == '.jpg':
                    cover_data = cf.read(name)
                    break
    elif original_file_extension.upper() == '.CBT':
        cf = tarfile.TarFile(tmp_file_name)
        for name in cf.getnames():
            ext = os.path.splitext(name)
            if len(ext) > 1:
                extension = ext[1].lower()
                if extension == '.jpg':
                    cover_data = cf.extractfile(name).read()
                    break

    prefix = os.path.dirname(tmp_file_name)
    if cover_data:
        tmp_cover_name = prefix + '/cover' + extension
        image = open(tmp_cover_name, 'wb')
        image.write(cover_data)
        image.close()
    else:
        tmp_cover_name = None
    return tmp_cover_name