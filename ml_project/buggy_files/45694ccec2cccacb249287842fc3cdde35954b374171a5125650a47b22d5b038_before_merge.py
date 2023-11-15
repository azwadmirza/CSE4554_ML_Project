def __create_playlist(name, pl_filename, files, library):
    playlist = FileBackedPlaylist.new(PLAYLISTS, name, library=library)
    songs = []
    win = WaitLoadWindow(
        None, len(files),
        _("Importing playlist.\n\n%(current)d/%(total)d songs added."))
    win.show()
    for i, filename in enumerate(files):
        if not uri_is_valid(filename):
            # Plain filename.
            songs.append(_af_for(filename, library, pl_filename))
        else:
            try:
                filename = uri2fsn(filename)
            except ValueError:
                # Who knows! Hand it off to GStreamer.
                songs.append(formats.remote.RemoteFile(filename))
            else:
                # URI-encoded local filename.
                songs.append(_af_for(filename, library, pl_filename))
        if win.step():
            break
    win.destroy()
    playlist.extend(filter(None, songs))
    return playlist