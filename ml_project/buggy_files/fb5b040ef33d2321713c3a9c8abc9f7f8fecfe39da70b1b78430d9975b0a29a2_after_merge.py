def sync_with_lutris():
    apps = get_games()
    desktop_games_in_lutris = pga.get_desktop_games()
    slugs_in_lutris = set([str(game['slug']) for game in desktop_games_in_lutris])

    seen_slugs = set()
    for app in apps:
        game_info = None
        name = app[0]
        appid = app[1]
        slug = slugify(name)

        # if it fails to get slug from the name
        if not slug:
            slug = slugify(appid)

        if not name or not slug or not appid:
            logger.error("Failed to load desktop game "
                         "\"" + str(name) + "\" "
                         "(app: " + str(appid) + ", slug: " + slug + ")")
            continue
        else:
            logger.debug("Found desktop game "
                         "\"" + str(name) + "\" "
                         "(app: " + str(appid) + ", slug: " + slug + ")")

        seen_slugs.add(slug)

        if slug not in slugs_in_lutris:
            game_info = {
                'name': name,
                'slug': slug,
                'config_path': slug + '-desktopapp',
                'installer_slug': 'desktopapp',
                'exe': app[2],
                'args': app[3]
            }
            mark_as_installed(appid, 'linux', game_info)

    unavailable_slugs = slugs_in_lutris.difference(seen_slugs)
    for slug in unavailable_slugs:
        for game in desktop_games_in_lutris:
            if game['slug'] == slug:
                mark_as_uninstalled(game)