def array_back(param, nodes, vul_function=None, file_path=None, isback=None):  # 回溯数组定义赋值
    """
    递归回溯数组赋值定义
    :param isback: 
    :param file_path: 
    :param vul_function: 
    :param param: 
    :param nodes: 
    :return: 
    """
    param_name = param.node.name
    param_expr = param.expr

    is_co = 3
    cp = param
    expr_lineno = 0

    # print nodes
    for node in nodes[::-1]:
        if isinstance(node, php.Assignment):
            param_node_name = get_node_name(node.node)
            param_node = node.node
            param_node_expr = node.expr

            if param_node_name == param_name:  # 处理数组中值被改变的问题
                if isinstance(node.expr, php.Array):
                    for p_node in node.expr.nodes:
                        if p_node.key == param_expr:
                            if isinstance(p_node.value, php.ArrayOffset):  # 如果赋值值仍然是数组，先经过判断在进入递归
                                is_co, cp = is_controllable(p_node.value.node.name)

                                if is_co != 1:
                                    is_co, cp, expr_lineno = array_back(param, nodes, file_path=file_path,
                                                                        isback=isback)

                            else:
                                n_node = php.Variable(p_node.value)
                                is_co, cp, expr_lineno = parameters_back(n_node, nodes, vul_function=vul_function,
                                                                         file_path=file_path,
                                                                         isback=isback)

            if param == param_node:  # 处理数组一次性赋值，左值为数组
                if isinstance(param_node_expr, php.ArrayOffset):  # 如果赋值值仍然是数组，先经过判断在进入递归
                    is_co, cp = is_controllable(param_node_expr.node.name)

                    if is_co != 1:
                        is_co, cp, expr_lineno = array_back(param, nodes, file_path=file_path,
                                                            isback=isback)
                else:
                    is_co, cp = is_controllable(param_node_expr)

                    if is_co != 1 and is_co != -1:
                        n_node = php.Variable(param_node_expr.node.value)
                        is_co, cp, expr_lineno = parameters_back(n_node, nodes, vul_function=vul_function,
                                                                 file_path=file_path,
                                                                 isback=isback)

    return is_co, cp, expr_lineno