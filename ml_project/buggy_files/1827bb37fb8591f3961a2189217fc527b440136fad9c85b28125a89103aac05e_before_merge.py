    def locate(
        visible_markers,
        camera_model,
        registered_markers_undist,
        registered_markers_dist,
    ):
        """Computes a Surface_Location based on a list of visible markers."""

        visible_registered_marker_ids = set(visible_markers.keys()) & set(
            registered_markers_undist.keys()
        )

        # If the surface is defined by 2+ markers, we require 2+ markers to be detected.
        # If the surface is defined by 1 marker, we require 1 marker to be detected.
        if not visible_registered_marker_ids or len(
            visible_registered_marker_ids
        ) < min(2, len(registered_markers_undist)):
            return Surface_Location(detected=False)

        visible_verts_dist = np.array(
            [visible_markers[id].verts_px for id in visible_registered_marker_ids]
        )
        registered_verts_undist = np.array(
            [
                registered_markers_undist[uid].verts_uv
                for uid in visible_registered_marker_ids
            ]
        )
        registered_verts_dist = np.array(
            [
                registered_markers_dist[uid].verts_uv
                for uid in visible_registered_marker_ids
            ]
        )

        visible_verts_dist.shape = (-1, 2)
        registered_verts_undist.shape = (-1, 2)
        registered_verts_dist.shape = (-1, 2)

        dist_img_to_surf_trans, surf_to_dist_img_trans = Surface._find_homographies(
            registered_verts_dist, visible_verts_dist
        )

        visible_verts_undist = camera_model.undistort_points_on_image_plane(
            visible_verts_dist
        )
        img_to_surf_trans, surf_to_img_trans = Surface._find_homographies(
            registered_verts_undist, visible_verts_undist
        )

        return Surface_Location(
            True,
            dist_img_to_surf_trans,
            surf_to_dist_img_trans,
            img_to_surf_trans,
            surf_to_img_trans,
            len(visible_registered_marker_ids),
        )