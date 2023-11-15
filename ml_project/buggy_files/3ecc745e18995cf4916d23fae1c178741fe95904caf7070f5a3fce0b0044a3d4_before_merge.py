    def _parse(track, **kwargs):
        returning = {}
        if (
            type(track) == type(LocalPath)
            and (track.is_file() or track.is_dir())
            and track.exists()
        ):
            returning["local"] = True
            returning["name"] = track.name
            if track.is_file():
                returning["single"] = True
            elif track.is_dir():
                returning["album"] = True
        else:
            track = str(track)
            if track.startswith("spotify:"):
                returning["spotify"] = True
                if ":playlist:" in track:
                    returning["playlist"] = True
                elif ":album:" in track:
                    returning["album"] = True
                elif ":track:" in track:
                    returning["single"] = True
                _id = track.split(":", 2)[-1]
                _id = _id.split("?")[0]
                returning["id"] = _id
                if "#" in _id:
                    match = re.search(_re_spotify_timestamp, track)
                    if match:
                        returning["start_time"] = (int(match.group(1)) * 60) + int(match.group(2))
                returning["uri"] = track
                return returning
            if track.startswith("sc ") or track.startswith("list "):
                if track.startswith("sc "):
                    returning["invoked_from"] = "sc search"
                    returning["soundcloud"] = True
                elif track.startswith("list "):
                    returning["invoked_from"] = "search list"
                track = _remove_start.sub("", track, 1)
                returning["queryforced"] = track

            _localtrack = LocalPath(track)
            if _localtrack.exists():
                if _localtrack.is_file():
                    returning["local"] = True
                    returning["single"] = True
                    returning["name"] = _localtrack.name
                    return returning
                elif _localtrack.is_dir():
                    returning["album"] = True
                    returning["local"] = True
                    returning["name"] = _localtrack.name
                    return returning
            try:
                query_url = urlparse(track)
                if all([query_url.scheme, query_url.netloc, query_url.path]):
                    url_domain = ".".join(query_url.netloc.split(".")[-2:])
                    if not query_url.netloc:
                        url_domain = ".".join(query_url.path.split("/")[0].split(".")[-2:])
                    if url_domain in ["youtube.com", "youtu.be"]:
                        returning["youtube"] = True
                        _has_index = "&index=" in track
                        if "&t=" in track:
                            match = re.search(_re_youtube_timestamp, track)
                            if match:
                                returning["start_time"] = int(match.group(1))
                        if _has_index:
                            match = re.search(_re_youtube_index, track)
                            if match:
                                returning["track_index"] = int(match.group(1)) - 1
                        if all(k in track for k in ["&list=", "watch?"]):
                            returning["track_index"] = 0
                            returning["playlist"] = True
                            returning["single"] = False
                        elif all(x in track for x in ["playlist?"]):
                            returning["playlist"] = not _has_index
                            returning["single"] = _has_index
                        elif any(k in track for k in ["list="]):
                            returning["track_index"] = 0
                            returning["playlist"] = True
                            returning["single"] = False
                        else:
                            returning["single"] = True
                    elif url_domain == "spotify.com":
                        returning["spotify"] = True
                        if "/playlist/" in track:
                            returning["playlist"] = True
                        elif "/album/" in track:
                            returning["album"] = True
                        elif "/track/" in track:
                            returning["single"] = True
                        val = re.sub(_re_spotify_url, "", track).replace("/", ":")
                        if "user:" in val:
                            val = val.split(":", 2)[-1]
                        _id = val.split(":", 1)[-1]
                        _id = _id.split("?")[0]

                        if "#" in _id:
                            _id = _id.split("#")[0]
                            match = re.search(_re_spotify_timestamp, track)
                            if match:
                                returning["start_time"] = (int(match.group(1)) * 60) + int(
                                    match.group(2)
                                )

                        returning["id"] = _id
                        returning["uri"] = f"spotify:{val}"
                    elif url_domain == "soundcloud.com":
                        returning["soundcloud"] = True
                        if "#t=" in track:
                            match = re.search(_re_soundcloud_timestamp, track)
                            if match:
                                returning["start_time"] = (int(match.group(1)) * 60) + int(
                                    match.group(2)
                                )
                        if "/sets/" in track:
                            if "?in=" in track:
                                returning["single"] = True
                            else:
                                returning["playlist"] = True
                        else:
                            returning["single"] = True
                    elif url_domain == "bandcamp.com":
                        returning["bandcamp"] = True
                        if "/album/" in track:
                            returning["album"] = True
                        else:
                            returning["single"] = True
                    elif url_domain == "vimeo.com":
                        returning["vimeo"] = True
                    elif url_domain in ["mixer.com", "beam.pro"]:
                        returning["mixer"] = True
                    elif url_domain == "twitch.tv":
                        returning["twitch"] = True
                        if "?t=" in track:
                            match = re.search(_re_twitch_timestamp, track)
                            if match:
                                returning["start_time"] = (
                                    (int(match.group(1)) * 60 * 60)
                                    + (int(match.group(2)) * 60)
                                    + int(match.group(3))
                                )

                        if not any(x in track for x in ["/clip/", "/videos/"]):
                            returning["stream"] = True
                    else:
                        returning["other"] = True
                        returning["single"] = True
                else:
                    if kwargs.get("soundcloud", False):
                        returning["soundcloud"] = True
                    else:
                        returning["youtube"] = True
                    returning["search"] = True
                    returning["single"] = True
            except Exception:
                returning["search"] = True
                returning["youtube"] = True
                returning["single"] = True
        return returning