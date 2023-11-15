    def allows(self, qual, loose=False):
        """Determine whether this set of requirements allows a given quality.

        :param Quality qual: The quality to evaluate.
        :param bool loose: If True, only ! (not) requirements will be enforced.
        :rtype: bool
        :returns: True if given quality passes all component requirements.
        """
        if isinstance(qual, basestring):
            qual = Quality(qual)
        for r_component, q_component in zip(self.components, qual.components):
            if not r_component.allows(q_component, loose=loose):
                return False
        return True