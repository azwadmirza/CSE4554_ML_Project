def create_thumbnail(fname, file_ext):
    thumb_size = (255, 160)
    thumb = Image.open(fname)
    thumb.thumbnail(thumb_size)
    thumb_hash = hashlib.sha256(thumb.tobytes()).hexdigest()
    thumbhashpath = f"{thumb_hash[0:2]}/{thumb_hash[2:4]}"
    thumbpath = os.path.join(
        current_app.config["MEDIA_DIRECTORY"], "thumbs", thumbhashpath
    )
    # makedirs attempts to make every directory necessary to get to the "thumbs" folder
    os.makedirs(thumbpath, exist_ok=True)
    fname = os.path.join(thumbpath, thumb_hash + file_ext)
    thumb.save(fname)
    thumb.close()
    return thumb_hash