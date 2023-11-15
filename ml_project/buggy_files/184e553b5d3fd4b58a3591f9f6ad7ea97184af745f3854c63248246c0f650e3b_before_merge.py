def concatenate_audioclips(clips):
    """
    The clip with the highest FPS will be the FPS of the result clip.
    """
    durations = [clip.duration for clip in clips]
    timings = np.cumsum([0] + durations)  # start times, and end time.
    newclips = [clip.with_start(t) for clip, t in zip(clips, timings)]

    result = CompositeAudioClip(newclips).with_duration(timings[-1])

    fpss = [clip.fps for clip in clips if getattr(clip, "fps", None)]
    result.fps = max(fpss) if fpss else None
    return result