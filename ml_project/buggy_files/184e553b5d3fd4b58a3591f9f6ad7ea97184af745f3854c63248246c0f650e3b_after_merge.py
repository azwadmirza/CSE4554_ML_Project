def concatenate_audioclips(clips):
    """Concatenates one AudioClip after another, in the order that are passed
    to ``clips`` parameter.

    Parameters
    ----------

    clips
      List of audio clips, which will be played one after other.
    """
    # start, end/start2, end2/start3... end
    starts_end = np.cumsum([0, *[clip.duration for clip in clips]])
    newclips = [clip.with_start(t) for clip, t in zip(clips, starts_end[:-1])]

    return CompositeAudioClip(newclips).with_duration(starts_end[-1])