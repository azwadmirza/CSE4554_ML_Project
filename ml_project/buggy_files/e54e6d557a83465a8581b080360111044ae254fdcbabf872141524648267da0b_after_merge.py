    def recalculate_kalman_filters(self, workspace, image_numbers):
        """Rerun the kalman filters to improve the motion models"""
        m = workspace.measurements
        object_name = self.object_name.value
        object_number = m[object_name, cpmeas.OBJECT_NUMBER, image_numbers]

        # ########################
        #
        # Create an indexer that lets you do the following
        #
        # parent_x = x[idx.fwd_idx[image_number - fi] + object_number - 1]
        # parent_y = y[idx.fwd_idx[image_number - fi] + object_number - 1]
        #
        # #######################
        x = m[object_name, M_LOCATION_CENTER_X, image_numbers]
        fi = np.min(image_numbers)
        max_image = np.max(image_numbers) + 1
        counts = np.zeros(max_image - fi, int)
        counts[image_numbers - fi] = np.array([len(xx) for xx in x])
        idx = Indexes(counts)
        x = np.hstack(x)
        y = np.hstack(m[object_name, M_LOCATION_CENTER_Y, image_numbers])
        area = np.hstack(m[object_name, self.measurement_name(F_AREA), image_numbers])
        parent_image_number = np.hstack(
            m[object_name, self.measurement_name(F_PARENT_IMAGE_NUMBER), image_numbers]
        ).astype(int)
        parent_object_number = np.hstack(
            m[object_name, self.measurement_name(F_PARENT_OBJECT_NUMBER), image_numbers]
        ).astype(int)
        link_type = np.hstack(
            m[object_name, self.measurement_name(F_LINK_TYPE), image_numbers]
        )
        link_distance = np.hstack(
            m[object_name, self.measurement_name(F_LINKING_DISTANCE), image_numbers]
        )
        movement_model = np.hstack(
            m[object_name, self.measurement_name(F_MOVEMENT_MODEL), image_numbers]
        )

        models = self.get_kalman_models()
        kalman_models = [
            cpfilter.static_kalman_model()
            if model == F_STATIC_MODEL
            else cpfilter.velocity_kalman_model()
            for model, elements in models
        ]
        kalman_states = [
            cpfilter.KalmanState(
                kalman_model.observation_matrix, kalman_model.translation_matrix
            )
            for kalman_model in kalman_models
        ]
        #
        # Initialize the last image set's states using no information
        #
        # TO_DO - use the kalman state information in the measurements
        #         to construct the kalman models that will best predict
        #         the penultimate image set.
        #
        n_objects = counts[-1]
        if n_objects > 0:
            this_slice = slice(idx.fwd_idx[-1], idx.fwd_idx[-1] + n_objects)
            ii = y[this_slice]
            jj = x[this_slice]
            new_kalman_states = []
            r = np.column_stack(
                (
                    area[this_slice].astype(float) / np.pi,
                    np.zeros(n_objects),
                    np.zeros(n_objects),
                    area[this_slice].astype(float),
                )
            ).reshape(n_objects, 2, 2)
            for kalman_state in kalman_states:
                new_kalman_states.append(
                    cpfilter.kalman_filter(
                        kalman_state,
                        -np.ones(n_objects, int),
                        np.column_stack((ii, jj)),
                        np.zeros(n_objects),
                        r,
                    )
                )
            kalman_states = new_kalman_states
        else:
            this_slice = slice(idx.fwd_idx[-1], idx.fwd_idx[-1])
        #
        # Update the kalman states and take any new linkage distances
        # and movement models that are better
        #
        for image_number in reversed(sorted(image_numbers)[:-1]):
            i = image_number - fi
            n_objects = counts[i]
            child_object_number = np.zeros(n_objects, int)
            next_slice = this_slice
            this_slice = slice(idx.fwd_idx[i], idx.fwd_idx[i] + counts[i])
            next_links = link_type[next_slice]
            next_has_link = next_links == LT_PHASE_1
            if any(next_has_link):
                next_parents = parent_object_number[next_slice]
                next_object_number = np.arange(counts[i + 1]) + 1
                child_object_number[
                    next_parents[next_has_link] - 1
                ] = next_object_number[next_has_link]
            has_child = child_object_number != 0
            if np.any(has_child):
                kid_idx = child_object_number[has_child] - 1
            ii = y[this_slice]
            jj = x[this_slice]
            r = np.column_stack(
                (
                    area[this_slice].astype(float) / np.pi,
                    np.zeros(n_objects),
                    np.zeros(n_objects),
                    area[this_slice].astype(float),
                )
            ).reshape(n_objects, 2, 2)
            new_kalman_states = []
            errors = link_distance[next_slice]
            model_used = movement_model[next_slice]
            for (model, elements), kalman_state in zip(models, kalman_states):
                assert isinstance(kalman_state, cpfilter.KalmanState)
                n_elements = len(elements)
                q = np.zeros((n_objects, n_elements, n_elements))
                if np.any(has_child):
                    obs = kalman_state.predicted_obs_vec
                    dk = np.sqrt(
                        (obs[kid_idx, 0] - ii[has_child]) ** 2
                        + (obs[kid_idx, 1] - jj[has_child]) ** 2
                    )
                    this_model = np.where(dk < errors[kid_idx])[0]
                    if len(this_model) > 0:
                        km_model = KM_NO_VEL if model == F_STATIC_MODEL else KM_VEL
                        model_used[kid_idx[this_model]] = km_model
                        errors[kid_idx[this_model]] = dk[this_model]

                    for j in range(n_elements):
                        q[has_child, j, j] = kalman_state.noise_var[kid_idx, j]
                updated_state = cpfilter.kalman_filter(
                    kalman_state,
                    child_object_number - 1,
                    np.column_stack((ii, jj)),
                    q,
                    r,
                )
                new_kalman_states.append(updated_state)
            if np.any(has_child):
                # fix child linking distances and models
                mname = self.measurement_name(F_LINKING_DISTANCE)
                m[object_name, mname, image_number + 1] = errors
                mname = self.measurement_name(F_MOVEMENT_MODEL)
                m[object_name, mname, image_number + 1] = model_used
            kalman_states = new_kalman_states