    def _select_mixer_track(self, mixer, track_label):
        # Ignore tracks without volumes, then look for track with
        # label == settings.MIXER_TRACK, otherwise fallback to first usable
        # track hoping the mixer gave them to us in a sensible order.

        usable_tracks = []
        for track in mixer.list_tracks():
            if not mixer.get_volume(track):
                continue

            if track_label and track.label == track_label:
                return track
            elif track.flags & (gst.interfaces.MIXER_TRACK_MASTER |
                                gst.interfaces.MIXER_TRACK_OUTPUT):
                usable_tracks.append(track)

        if usable_tracks:
            return usable_tracks[0]