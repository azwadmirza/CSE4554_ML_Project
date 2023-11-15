    def __init__(self, pose_relation=PoseRelation.translation_part, delta=1.0,
                 delta_unit=Unit.frames, rel_delta_tol=0.1, all_pairs=False):
        if delta < 0:
            raise MetricsException("delta must be a positive number")
        if delta_unit == Unit.frames and not isinstance(delta, int) \
                and not delta.is_integer():
            raise MetricsException(
                "delta must be integer for delta unit {}".format(delta_unit))
        self.delta = int(delta) if delta_unit == Unit.frames else delta
        self.delta_unit = delta_unit
        self.rel_delta_tol = rel_delta_tol
        self.pose_relation = pose_relation
        self.all_pairs = all_pairs
        self.E = []
        self.error = []
        self.delta_ids = []
        if pose_relation == PoseRelation.translation_part:
            self.unit = Unit.meters
        elif pose_relation == PoseRelation.rotation_angle_deg:
            self.unit = Unit.degrees
        elif pose_relation == PoseRelation.rotation_angle_rad:
            self.unit = Unit.radians
        else:
            # dimension-less
            self.unit = Unit.none