def find_icon_path_zip(res_dir, icon_paths_from_manifest):
    """Tries to find an icon, based on paths fetched from the manifest and by global search
        returns an empty string on fail or a full path"""
    global KNOWN_MIPMAP_SIZES
    try:
        logger.info("Guessing icon path")
        for icon_path in icon_paths_from_manifest:
            if icon_path.startswith('@'):
                path_array = icon_path.strip('@').split(os.sep)
                rel_path = os.sep.join(path_array[1:])
                for size_str in KNOWN_MIPMAP_SIZES:
                    tmp_path = os.path.join(
                        res_dir, path_array[0] + size_str, rel_path + '.png')
                    if os.path.exists(tmp_path):
                        return tmp_path
            else:
                if icon_path.starswith('res/') or icon_path.starswith('/res/'):
                    stripped_relative_path = icon_path.strip(
                        '/res')  # Works for neither /res and res
                    full_path = os.path.join(res_dir, stripped_relative_path)
                    if os.path.exists(full_path):
                        return full_path
                    full_path += '.png'
                    if os.path.exists(full_path):
                        return full_path

            file_name = icon_path.split(os.sep)[-1]
            if file_name.endswith('.png'):
                file_name += '.png'

            for guess in search_folder(res_dir, file_name):
                if os.path.exists(guess):
                    return guess

        # If didn't find, try the default name.. returns empty if not find
        return guess_icon_path(res_dir)

    except:
        PrintException("[ERROR] Guessing icon path")