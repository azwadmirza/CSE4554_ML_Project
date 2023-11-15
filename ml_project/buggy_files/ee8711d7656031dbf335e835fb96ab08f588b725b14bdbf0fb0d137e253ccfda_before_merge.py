def extractCover(tmp_file_name, original_file_extension):
    if original_file_extension.upper() == '.CBZ':
        cf = zipfile.ZipFile(tmp_file_name)
        compressed_name = cf.namelist()[0]
        cover_data = cf.read(compressed_name)
    elif original_file_extension.upper() == '.CBT':
        cf = tarfile.TarFile(tmp_file_name)
        compressed_name = cf.getnames()[0]
        cover_data = cf.extractfile(compressed_name).read()

    prefix = os.path.dirname(tmp_file_name)

    tmp_cover_name = prefix + '/cover' + os.path.splitext(compressed_name)[1]
    image = open(tmp_cover_name, 'wb')
    image.write(cover_data)
    image.close()
    return tmp_cover_name