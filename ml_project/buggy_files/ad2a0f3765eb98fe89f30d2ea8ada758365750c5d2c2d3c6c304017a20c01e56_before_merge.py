    def _add_timeslots(self,
                       time: int,
                       schedule: Union['Schedule', Instruction]) -> None:
        """Update all time tracking within this schedule based on the given schedule.

        Args:
            time: The time to insert the schedule into self.
            schedule: The schedule to insert into self.

        Raises:
            PulseError: If timeslots overlap or an invalid start time is provided.
        """
        if not isinstance(time, int):
            raise PulseError("Schedule start time must be an integer.")

        other_timeslots = _get_timeslots(schedule)
        self._duration = max(self._duration, time + schedule.duration)

        for channel in schedule.channels:
            if channel not in self._timeslots:
                if time == 0:
                    self._timeslots[channel] = copy.copy(other_timeslots[channel])
                else:
                    self._timeslots[channel] = [(i[0] + time, i[1] + time)
                                                for i in other_timeslots[channel]]
                continue

            for idx, interval in enumerate(other_timeslots[channel]):
                if interval[0] + time >= self._timeslots[channel][-1][1]:
                    # Can append the remaining intervals
                    self._timeslots[channel].extend(
                        [(i[0] + time, i[1] + time)
                         for i in other_timeslots[channel][idx:]])
                    break

                try:
                    interval = (interval[0] + time, interval[1] + time)
                    index = _find_insertion_index(self._timeslots[channel], interval)
                    self._timeslots[channel].insert(index, interval)
                except PulseError:
                    raise PulseError(
                        "Schedule(name='{new}') cannot be inserted into Schedule(name='{old}') at "
                        "time {time} because its instruction on channel {ch} scheduled from time "
                        "{t0} to {tf} overlaps with an existing instruction."
                        "".format(new=schedule.name or '', old=self.name or '', time=time,
                                  ch=channel, t0=interval[0], tf=interval[1]))

        _check_nonnegative_timeslot(self._timeslots)