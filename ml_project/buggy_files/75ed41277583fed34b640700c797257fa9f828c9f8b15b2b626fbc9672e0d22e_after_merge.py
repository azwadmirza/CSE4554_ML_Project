    def label(self) -> str:
        """The name given by the user to the device.

        Note: labels are shown to the user to help distinguish their devices,
        and they are also used as a fallback to distinguish devices programmatically.
        So ideally, different devices would have different labels.
        """
        raise NotImplementedError()