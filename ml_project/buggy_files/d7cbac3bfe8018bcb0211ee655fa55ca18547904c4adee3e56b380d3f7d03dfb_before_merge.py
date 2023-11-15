def process_screenshots(screenshots):
    # Handle screenshots

    num_screenshots = 0
    for item in screenshots:
        if item["service"] == "VNC":
            file_ext = ".jpg"
        else:  # Handles http, https files from aquatone/chromium-headless
            file_ext = ".png"

        image = base64.b64decode(item["data"])
        image_hash = hashlib.sha256(image).hexdigest()

        hashpath = f"{image_hash[0:2]}/{image_hash[2:4]}"
        dirpath = os.path.join(
            current_app.config["MEDIA_DIRECTORY"], "original", hashpath
        )

        # makedirs attempts to make every directory necessary to get to the "original" folder
        os.makedirs(dirpath, exist_ok=True)

        fname = os.path.join(dirpath, image_hash + file_ext)
        with open(fname, "wb") as f:
            f.write(image)
        item["hash"] = image_hash
        del item["data"]

        item["thumb_hash"] = create_thumbnail(fname, file_ext)
        num_screenshots += 1

    return screenshots, num_screenshots