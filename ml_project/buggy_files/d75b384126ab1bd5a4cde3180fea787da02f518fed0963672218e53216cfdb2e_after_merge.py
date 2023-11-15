    def _find_homographies(points_A, points_B):
        points_A = points_A.reshape((-1, 1, 2))
        points_B = points_B.reshape((-1, 1, 2))

        B_to_A, mask = cv2.findHomography(points_A, points_B)
        # NOTE: cv2.findHomography(A, B) will not produce the inverse of
        # cv2.findHomography(B, A)! The errors can actually be quite large, resulting in
        # on-screen discrepancies of up to 50 pixels. We try to find the inverse
        # analytically instead with fallbacks.

        try:
            A_to_B = np.linalg.inv(B_to_A)
            return A_to_B, B_to_A
        except np.linalg.LinAlgError as e:
            pass
        except Exception as e:
            import traceback
            exception_msg = traceback.format_exc()
            logger.error(exception_msg)

        logger.debug(
            "Failed to calculate inverse homography with np.inv()! "
            "Trying with np.pinv() instead."
        )

        try:
            A_to_B = np.linalg.pinv(B_to_A)
            return A_to_B, B_to_A
        except np.linalg.LinAlgError as e:
            pass
        except Exception as e:
            import traceback
            exception_msg = traceback.format_exc()
            logger.error(exception_msg)

        logger.warning(
            "Failed to calculate inverse homography with np.pinv()! "
            "Falling back to inaccurate manual computation!"
        )

        A_to_B, mask = cv2.findHomography(points_B, points_A)
        return A_to_B, B_to_A