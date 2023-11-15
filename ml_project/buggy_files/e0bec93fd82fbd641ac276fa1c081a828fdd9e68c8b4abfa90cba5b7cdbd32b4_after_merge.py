    def istp(self):
        
        if self.type in ["super", "oper"]:
            try:
                q_oper = sr.to_choi(self)
                # We use the condition from John Watrous' lecture notes,
                # Tr_1(J(Phi)) = identity_2.
                tr_oper = ptrace(q_oper, (0,))
                ident = ops.identity(tr_oper.shape[0])
                
                return isequal(tr_oper, ident)
            except:
                return False
        else:
            return False