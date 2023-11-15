def feed_playlist(username):
    # fetch all user playlists
    playlists = spotify.user_playlists(username)
    links = []
    check = 1
    # iterate over user playlists
    while True:
        for playlist in playlists['items']:
            # In rare cases, playlists may not be found, so playlists['next'] is
            # None. Skip these. Also see Issue #91.
            if playlist['name'] is not None:
                print(str(check) + '. ' + misc.fix_encoding(playlist['name']) + ' (' + str(playlist['tracks']['total']) + ' tracks)')
                links.append(playlist)
                check += 1
        if playlists['next']:
            playlists = spotify.next(playlists)
        else:
            break

    print('')
    # let user select playlist
    playlist = misc.input_link(links)
    # fetch detailed information for playlist
    results = spotify.user_playlist(playlist['owner']['id'], playlist['id'], fields="tracks,next")
    print('')
    # slugify removes any special characters
    file = slugify(playlist['name'], ok='-_()[]{}') + '.txt'
    print('Feeding ' + str(playlist['tracks']['total']) + ' tracks to ' + file)

    tracks = results['tracks']
    with open(file, 'a') as fout:
        while True:
            for item in tracks['items']:
                track = item['track']
                try:
                    fout.write(track['external_urls']['spotify'] + '\n')
                except KeyError:
                    title = track['name'] + ' by '+ track['artists'][0]['name']
                    print('Skipping track ' + title + ' (local only?)')
            # 1 page = 50 results
            # check if there are more pages
            if tracks['next']:
                tracks = spotify.next(tracks)
            else:
                break