def evaluate_var(xss_var, parent, until, ignore_nodes=None):
    secure = False
    if isinstance(xss_var, ast.Name):
        if isinstance(parent, ast.FunctionDef):
            for name in parent.args.args:
                if name.id == xss_var.id:
                    return False  # Params are not secure

        analyser = DeepAssignation(xss_var, ignore_nodes)
        for node in parent.body:
            if node.lineno >= until:
                break
            to = analyser.is_assigned(node)
            if to:
                if isinstance(to, ast.Str):
                    secure = True
                elif isinstance(to, ast.Name):
                    secure = evaluate_var(to, parent,
                                          to.lineno, ignore_nodes)
                elif isinstance(to, ast.Call):
                    secure = evaluate_call(to, parent, ignore_nodes)
                elif isinstance(to, (list, tuple)):
                    num_secure = 0
                    for some_to in to:
                        if isinstance(some_to, ast.Str):
                            num_secure += 1
                        elif isinstance(some_to, ast.Name):
                            if evaluate_var(some_to, parent,
                                            node.lineno, ignore_nodes):
                                num_secure += 1
                            else:
                                break
                        else:
                            break
                    if num_secure == len(to):
                        secure = True
                    else:
                        secure = False
                        break
                else:
                    secure = False
                    break
    return secure