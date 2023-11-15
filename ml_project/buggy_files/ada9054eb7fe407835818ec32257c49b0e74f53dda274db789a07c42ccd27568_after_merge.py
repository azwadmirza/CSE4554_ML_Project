def advanced_settings():

    ''' Track the existence of <cleanonupdate>true</cleanonupdate>
        It is incompatible with plugin paths.
    '''
    if settings('useDirectPaths') != "0":
        return

    path = xbmc.translatePath("special://profile/")
    file = os.path.join(path, 'advancedsettings.xml')

    try:
        xml = etree.parse(file).getroot()
    except Exception:
        return

    video = xml.find('videolibrary')

    if video is not None:
        cleanonupdate = video.find('cleanonupdate')

        if cleanonupdate is not None and cleanonupdate.text == "true":

            LOG.warning("cleanonupdate disabled")
            video.remove(cleanonupdate)

            tree = etree.ElementTree(xml)
            tree.write(file)

            dialog("ok", "{jellyfin}", translate(33097))
            xbmc.executebuiltin('RestartApp')

            return True