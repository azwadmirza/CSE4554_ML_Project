        def key(obj):
            poly, exp = obj
            rep = poly.rep.rep
            return (len(rep), exp, rep)