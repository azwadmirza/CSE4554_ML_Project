    def _eval_Eq(self, other):
        if not other.is_FiniteSet:
            if (other.is_Union or other.is_Complement or
                other.is_Intersection or other.is_ProductSet):
                return

            return false

        if len(self) != len(other):
            return false

        return And(*map(lambda x, y: Eq(x, y), self.args, other.args))