    def _satisfies_target(self, other_target, strict):
        self_target = self.target

        need_to_check = bool(other_target) if strict or self.concrete \
            else bool(other_target and self_target)

        # If there's no need to check we are fine
        if not need_to_check:
            return True

        # self is not concrete, but other_target is there and strict=True
        if self.target is None:
            return False

        for target_range in str(other_target).split(','):
            t_min, sep, t_max = target_range.partition(':')

            # Checking against a single specific target
            if not sep and self_target == t_min:
                return True

            if not sep and self_target != t_min:
                return False

            # Check against a range
            min_ok = self_target.microarchitecture >= t_min if t_min else True
            max_ok = self_target.microarchitecture <= t_max if t_max else True

            if min_ok and max_ok:
                return True

        return False