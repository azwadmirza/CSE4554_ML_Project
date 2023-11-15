def Restore(mirror_rp, inc_rpath, target, restore_to_time):
    """Recursively restore mirror and inc_rpath to target at rest_time"""
    MirrorS = mirror_rp.conn.restore.MirrorStruct
    TargetS = target.conn.restore.TargetStruct

    MirrorS.set_mirror_and_rest_times(restore_to_time)
    MirrorS.initialize_rf_cache(mirror_rp, inc_rpath)
    target_iter = TargetS.get_initial_iter(target)
    diff_iter = MirrorS.get_diffs(target_iter)
    TargetS.patch(target, diff_iter)
    MirrorS.close_rf_cache()