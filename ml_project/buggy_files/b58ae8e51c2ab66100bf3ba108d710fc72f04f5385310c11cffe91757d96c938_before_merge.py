    def iscptp(self):

        if self.type == "super" or self.type == "oper":
            q_oper = sr.to_choi(self)
            return q_oper.iscp and q_oper.istp
        else:
            return False