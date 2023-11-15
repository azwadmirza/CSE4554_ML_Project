def run(args):
    import os
    import sys

    import numpy as np

    import evo.core.lie_algebra as lie
    from evo.core import trajectory
    from evo.core.trajectory import PoseTrajectory3D
    from evo.tools import file_interface, log
    from evo.tools.settings import SETTINGS

    log.configure_logging(verbose=args.verbose, silent=args.silent,
                          debug=args.debug, local_logfile=args.logfile)
    if args.debug:
        import pprint
        logger.debug("main_parser config:\n" + pprint.pformat(
            {arg: getattr(args, arg)
             for arg in vars(args)}) + "\n")
    logger.debug(SEP)

    trajectories, ref_traj = load_trajectories(args)

    if args.merge:
        if args.subcommand == "kitti":
            die("Can't merge KITTI files.")
        if len(trajectories) == 0:
            die("No trajectories to merge (excluding --ref).")
        trajectories = {
            "merged_trajectory": trajectory.merge(trajectories.values())
        }

    if args.transform_left or args.transform_right:
        tf_type = "left" if args.transform_left else "right"
        tf_path = args.transform_left \
                if args.transform_left else args.transform_right
        transform = file_interface.load_transform_json(tf_path)
        logger.debug(SEP)
        if not lie.is_se3(transform):
            logger.warning("Not a valid SE(3) transformation!")
        if args.invert_transform:
            transform = lie.se3_inverse(transform)
        logger.debug("Applying a {}-multiplicative transformation:\n{}".format(
            tf_type, transform))
        for traj in trajectories.values():
            traj.transform(transform, right_mul=args.transform_right,
                           propagate=args.propagate_transform)

    if args.t_offset:
        logger.debug(SEP)
        for name, traj in trajectories.items():
            if type(traj) is trajectory.PosePath3D:
                die("{} doesn't have timestamps - can't add time offset.".
                    format(name))
            logger.info("Adding time offset to {}: {} (s)".format(
                name, args.t_offset))
            traj.timestamps += args.t_offset

    if args.n_to_align != -1 and not (args.align or args.correct_scale):
        die("--n_to_align is useless without --align or/and --correct_scale")

    if args.sync or args.align or args.correct_scale or args.align_origin:
        from evo.core import sync
        if not args.ref:
            logger.debug(SEP)
            die("Can't align or sync without a reference! (--ref)  *grunt*")
        for name, traj in trajectories.items():
            if args.subcommand == "kitti":
                ref_traj_tmp = ref_traj
            else:
                logger.debug(SEP)
                ref_traj_tmp, trajectories[name] = sync.associate_trajectories(
                    ref_traj, traj, max_diff=args.t_max_diff,
                    first_name="reference", snd_name=name)
            if args.align or args.correct_scale:
                logger.debug(SEP)
                logger.debug("Aligning {} to reference.".format(name))
                trajectories[name] = trajectory.align_trajectory(
                    trajectories[name], ref_traj_tmp,
                    correct_scale=args.correct_scale,
                    correct_only_scale=args.correct_scale and not args.align,
                    n=args.n_to_align)
            if args.align_origin:
                logger.debug(SEP)
                logger.debug("Aligning {}'s origin to reference.".format(name))
                trajectories[name] = trajectory.align_trajectory_origin(
                    trajectories[name], ref_traj_tmp)

    print_compact_name = not args.subcommand == "bag"
    for name, traj in trajectories.items():
        print_traj_info(name, traj, args.verbose, args.full_check,
                        print_compact_name)
    if args.ref:
        print_traj_info(args.ref, ref_traj, args.verbose, args.full_check,
                        print_compact_name)

    if args.plot or args.save_plot or args.serialize_plot:
        import numpy as np
        from evo.tools import plot
        import matplotlib.pyplot as plt
        import matplotlib.cm as cm

        plot_collection = plot.PlotCollection("evo_traj - trajectory plot")
        fig_xyz, axarr_xyz = plt.subplots(3, sharex="col", figsize=tuple(
            SETTINGS.plot_figsize))
        fig_rpy, axarr_rpy = plt.subplots(3, sharex="col", figsize=tuple(
            SETTINGS.plot_figsize))
        fig_traj = plt.figure(figsize=tuple(SETTINGS.plot_figsize))

        plot_mode = plot.PlotMode[args.plot_mode]
        ax_traj = plot.prepare_axis(fig_traj, plot_mode)

        if args.ref:
            short_traj_name = os.path.splitext(os.path.basename(args.ref))[0]
            if SETTINGS.plot_usetex:
                short_traj_name = short_traj_name.replace("_", "\\_")
            plot.traj(ax_traj, plot_mode, ref_traj,
                      style=SETTINGS.plot_reference_linestyle,
                      color=SETTINGS.plot_reference_color,
                      label=short_traj_name,
                      alpha=SETTINGS.plot_reference_alpha)
            plot.draw_coordinate_axes(ax_traj, ref_traj, plot_mode,
                                      SETTINGS.plot_axis_marker_scale)
            plot.traj_xyz(
                axarr_xyz, ref_traj, style=SETTINGS.plot_reference_linestyle,
                color=SETTINGS.plot_reference_color, label=short_traj_name,
                alpha=SETTINGS.plot_reference_alpha)
            plot.traj_rpy(
                axarr_rpy, ref_traj, style=SETTINGS.plot_reference_linestyle,
                color=SETTINGS.plot_reference_color, label=short_traj_name,
                alpha=SETTINGS.plot_reference_alpha)

        if args.ros_map_yaml:
            plot.ros_map(ax_traj, args.ros_map_yaml, plot_mode)

        cmap_colors = None
        if SETTINGS.plot_multi_cmap.lower() != "none":
            cmap = getattr(cm, SETTINGS.plot_multi_cmap)
            cmap_colors = iter(cmap(np.linspace(0, 1, len(trajectories))))

        for name, traj in trajectories.items():
            if cmap_colors is None:
                color = next(ax_traj._get_lines.prop_cycler)['color']
            else:
                color = next(cmap_colors)
            if print_compact_name:
                short_traj_name = os.path.splitext(os.path.basename(name))[0]
            else:
                short_traj_name = name
            if SETTINGS.plot_usetex:
                short_traj_name = short_traj_name.replace("_", "\\_")
            plot.traj(ax_traj, plot_mode, traj,
                      SETTINGS.plot_trajectory_linestyle, color,
                      short_traj_name, alpha=SETTINGS.plot_trajectory_alpha)
            plot.draw_coordinate_axes(ax_traj, traj, plot_mode,
                                      SETTINGS.plot_axis_marker_scale)
            if args.ref and isinstance(ref_traj, trajectory.PoseTrajectory3D):
                start_time = ref_traj.timestamps[0]
            else:
                start_time = None
            plot.traj_xyz(axarr_xyz, traj, SETTINGS.plot_trajectory_linestyle,
                          color, short_traj_name,
                          alpha=SETTINGS.plot_trajectory_alpha,
                          start_timestamp=start_time)
            plot.traj_rpy(axarr_rpy, traj, SETTINGS.plot_trajectory_linestyle,
                          color, short_traj_name,
                          alpha=SETTINGS.plot_trajectory_alpha,
                          start_timestamp=start_time)
            if not SETTINGS.plot_usetex:
                fig_rpy.text(0., 0.005, "euler_angle_sequence: {}".format(
                    SETTINGS.euler_angle_sequence), fontsize=6)

        plot_collection.add_figure("trajectories", fig_traj)
        plot_collection.add_figure("xyz_view", fig_xyz)
        plot_collection.add_figure("rpy_view", fig_rpy)
        if args.plot:
            plot_collection.show()
        if args.save_plot:
            logger.info(SEP)
            plot_collection.export(args.save_plot,
                                   confirm_overwrite=not args.no_warnings)
        if args.serialize_plot:
            logger.info(SEP)
            plot_collection.serialize(args.serialize_plot,
                                      confirm_overwrite=not args.no_warnings)

    if args.save_as_tum:
        logger.info(SEP)
        for name, traj in trajectories.items():
            dest = os.path.splitext(os.path.basename(name))[0] + ".tum"
            file_interface.write_tum_trajectory_file(
                dest, traj, confirm_overwrite=not args.no_warnings)
        if args.ref:
            dest = os.path.splitext(os.path.basename(args.ref))[0] + ".tum"
            file_interface.write_tum_trajectory_file(
                dest, ref_traj, confirm_overwrite=not args.no_warnings)
    if args.save_as_kitti:
        logger.info(SEP)
        for name, traj in trajectories.items():
            dest = os.path.splitext(os.path.basename(name))[0] + ".kitti"
            file_interface.write_kitti_poses_file(
                dest, traj, confirm_overwrite=not args.no_warnings)
        if args.ref:
            dest = os.path.splitext(os.path.basename(args.ref))[0] + ".kitti"
            file_interface.write_kitti_poses_file(
                dest, ref_traj, confirm_overwrite=not args.no_warnings)
    if args.save_as_bag:
        import datetime
        import rosbag
        dest_bag_path = str(
            datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + ".bag"
        logger.info(SEP)
        logger.info("Saving trajectories to " + dest_bag_path + "...")
        bag = rosbag.Bag(dest_bag_path, 'w')
        try:
            for name, traj in trajectories.items():
                dest_topic = os.path.splitext(os.path.basename(name))[0]
                frame_id = traj.meta[
                    "frame_id"] if "frame_id" in traj.meta else ""
                file_interface.write_bag_trajectory(bag, traj, dest_topic,
                                                    frame_id)
            if args.ref:
                dest_topic = os.path.splitext(os.path.basename(args.ref))[0]
                frame_id = ref_traj.meta[
                    "frame_id"] if "frame_id" in ref_traj.meta else ""
                file_interface.write_bag_trajectory(bag, ref_traj, dest_topic,
                                                    frame_id)
        finally:
            bag.close()