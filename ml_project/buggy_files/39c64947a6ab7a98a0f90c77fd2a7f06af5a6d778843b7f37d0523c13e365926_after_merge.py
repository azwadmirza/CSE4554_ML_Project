    def is_keys_unchanged(self, current_objects: Set[str]) -> bool:
        """
        Checks whether new objects have been uploaded and the inactivity_period
        has passed and updates the state of the sensor accordingly.

        :param current_objects: set of object ids in bucket during last poke.
        :type current_objects: set[str]
        """
        current_num_objects = len(current_objects)
        if current_objects > self.previous_objects:
            # When new objects arrived, reset the inactivity_seconds
            # and update previous_objects for the next poke.
            self.log.info(
                "New objects found at %s, resetting last_activity_time.",
                os.path.join(self.bucket_name, self.prefix),
            )
            self.log.debug("New objects: %s", current_objects - self.previous_objects)
            self.last_activity_time = datetime.now()
            self.inactivity_seconds = 0
            self.previous_objects = current_objects
            return False

        if self.previous_objects - current_objects:
            # During the last poke interval objects were deleted.
            if self.allow_delete:
                deleted_objects = self.previous_objects - current_objects
                self.previous_objects = current_objects
                self.last_activity_time = datetime.now()
                self.log.info(
                    "Objects were deleted during the last poke interval. Updating the "
                    "file counter and resetting last_activity_time:\n%s",
                    deleted_objects,
                )
                return False

            raise AirflowException(
                "Illegal behavior: objects were deleted in %s between pokes."
                % os.path.join(self.bucket_name, self.prefix)
            )

        if self.last_activity_time:
            self.inactivity_seconds = int((datetime.now() - self.last_activity_time).total_seconds())
        else:
            # Handles the first poke where last inactivity time is None.
            self.last_activity_time = datetime.now()
            self.inactivity_seconds = 0

        if self.inactivity_seconds >= self.inactivity_period:
            path = os.path.join(self.bucket_name, self.prefix)

            if current_num_objects >= self.min_objects:
                self.log.info(
                    "SUCCESS: \nSensor found %s objects at %s.\n"
                    "Waited at least %s seconds, with no new objects uploaded.",
                    current_num_objects,
                    path,
                    self.inactivity_period,
                )
                return True

            self.log.error("FAILURE: Inactivity Period passed, not enough objects found in %s", path)

            return False
        return False