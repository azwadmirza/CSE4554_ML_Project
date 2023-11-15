    def _get_free_pos(cls, instance=None):
        """Skips specified instance"""
        positions = set(abs(inst.pos) for inst in cls._instances
                        if inst is not instance)
        return min(set(range(len(positions) + 1)).difference(positions))