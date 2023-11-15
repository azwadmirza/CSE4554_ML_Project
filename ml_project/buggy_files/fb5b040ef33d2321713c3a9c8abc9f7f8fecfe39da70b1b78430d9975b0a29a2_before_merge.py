def sync_with_lutris():
    apps = get_games()
    desktop_games_in_lutris = pga.get_desktop_games()
    slugs_in_lutris = set([str(game['slug']) for game in desktop_games_in_lutris])

    seen_slugs = set()
    for app in apps:
        game_info = None
        name = app[0]
        slug = slugify(name)
        appid = app[1]

        if not name or not slug or not appid:
            logger.error("Failed to load desktop game "
                         "\"" + str(name) + "\" (" + str(appid) + ".desktop)")
            continue
        else:
            logger.debug("Found desktop game "
                         "\"" + str(name) + "\" (" + str(appid) + ".desktop)")

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