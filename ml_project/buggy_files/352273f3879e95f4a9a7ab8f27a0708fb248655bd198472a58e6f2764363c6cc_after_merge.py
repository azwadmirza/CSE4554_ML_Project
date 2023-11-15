    def iscp(self):
        # FIXME: this needs to be cached in the same ways as isherm.
        if self.type in ["super", "oper"]:
            try:
                q_oper = sr.to_choi(self)
                eigs = q_oper.eigenenergies()
                return all(eigs >= 0)
            except:
                return False
        else:
            return False