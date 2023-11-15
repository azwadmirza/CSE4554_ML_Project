    def styleSheet(self) -> Optional[StyleSheet]:
        return next(self.model.select(StyleSheet), None)