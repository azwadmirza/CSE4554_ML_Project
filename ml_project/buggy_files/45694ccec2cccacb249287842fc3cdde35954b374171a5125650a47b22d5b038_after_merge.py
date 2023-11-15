def __create_playlist(name, source_dir, files, library):
    playlist = FileBackedPlaylist.new(PLAYLISTS, name, library=library)
    print_d("Created playlist %s" % playlist)
    songs = []
    win = WaitLoadWindow(
        None, len(files),
        _("Importing playlist.\n\n%(current)d/%(total)d songs added."))
    win.show()
    for i, filename in enumerate(files):
        if not uri_is_valid(filename):
            # Plain filename.
            songs.append(_af_for(filename, library, source_dir))
        else:
            try:
                filename = uri2fsn(filename)
            except ValueError:
                # Who knows! Hand it off to GStreamer.
                songs.append(formats.remote.RemoteFile(filename))
            else:
                # URI-encoded local filename.
                songs.append(_af_for(filename, library, source_dir))
        if win.step():
            break
    win.destroy()
    playlist.extend(listfilter(None, songs))
    return playlist