        def visit_enum(self, enum):
            if not self._can_drop_enum(enum):
                return

            self.connection.execute(DropEnumType(enum))