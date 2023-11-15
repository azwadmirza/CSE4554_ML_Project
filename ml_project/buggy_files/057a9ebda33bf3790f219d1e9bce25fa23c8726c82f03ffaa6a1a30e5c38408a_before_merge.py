    def add_transform_to_subject_history(self, subject):
        from .augmentation import RandomTransform
        from . import Compose, OneOf, CropOrPad, EnsureShapeMultiple
        from .preprocessing.label import SequentialLabels
        call_others = (
            RandomTransform,
            Compose,
            OneOf,
            CropOrPad,
            EnsureShapeMultiple,
            SequentialLabels,
        )
        if not isinstance(self, call_others):
            subject.add_transform(self, self._get_reproducing_arguments())