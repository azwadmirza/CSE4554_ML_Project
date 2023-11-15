def create_thumbnail(fname, file_ext):
    thumb_size = (255, 160)
    thumb = Image.open(fname)
    thumb.thumbnail(thumb_size)
    thumb_hash = hashlib.sha256(thumb.tobytes()).hexdigest()
    fname = get_file_path(thumb_hash, "thumbs", file_ext)
    thumb.save(fname)
    thumb.close()
    return thumb_hash