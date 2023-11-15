    def detect_and_extract(self, image):
        """Detect oriented FAST keypoints and extract rBRIEF descriptors.

        Note that this is faster than first calling `detect` and then
        `extract`.

        Parameters
        ----------
        image : 2D array
            Input image.

        """
        assert_nD(image, 2)

        pyramid = self._build_pyramid(image)

        keypoints_list = []
        responses_list = []
        scales_list = []
        orientations_list = []
        descriptors_list = []

        for octave in range(len(pyramid)):

            octave_image = np.ascontiguousarray(pyramid[octave])

            keypoints, orientations, responses = \
                self._detect_octave(octave_image)

            if len(keypoints) == 0:
                keypoints_list.append(keypoints)
                responses_list.append(responses)
                descriptors_list.append(np.zeros((0, 256), dtype=np.bool))
                continue

            descriptors, mask = self._extract_octave(octave_image, keypoints,
                                                     orientations)

            keypoints_list.append(keypoints[mask] * self.downscale ** octave)
            responses_list.append(responses[mask])
            orientations_list.append(orientations[mask])
            scales_list.append(self.downscale ** octave
                               * np.ones(keypoints.shape[0], dtype=np.intp))
            descriptors_list.append(descriptors)

        keypoints = np.vstack(keypoints_list)
        responses = np.hstack(responses_list)
        scales = np.hstack(scales_list)
        orientations = np.hstack(orientations_list)
        descriptors = np.vstack(descriptors_list).view(np.bool)

        if keypoints.shape[0] < self.n_keypoints:
            self.keypoints = keypoints
            self.scales = scales
            self.orientations = orientations
            self.responses = responses
            self.descriptors = descriptors
        else:
            # Choose best n_keypoints according to Harris corner response
            best_indices = responses.argsort()[::-1][:self.n_keypoints]
            self.keypoints = keypoints[best_indices]
            self.scales = scales[best_indices]
            self.orientations = orientations[best_indices]
            self.responses = responses[best_indices]
            self.descriptors = descriptors[best_indices]