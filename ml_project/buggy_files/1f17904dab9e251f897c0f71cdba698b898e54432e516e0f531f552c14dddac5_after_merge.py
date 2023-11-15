    def _parse_variable_definition(self, statement, node):
        try:
            local_var = LocalVariableSolc(statement)
            local_var.set_function(self)
            local_var.set_offset(statement['src'], self.contract.slither)

            self._add_local_variable(local_var)
            #local_var.analyze(self)

            new_node = self._new_node(NodeType.VARIABLE, statement['src'])
            new_node.add_variable_declaration(local_var)
            link_nodes(node, new_node)
            return new_node
        except MultipleVariablesDeclaration:
            # Custom handling of var (a,b) = .. style declaration
            if self.is_compact_ast:
                variables = statement['declarations']
                count = len(variables)

                if statement['initialValue']['nodeType'] == 'TupleExpression':
                    inits = statement['initialValue']['components']
                    i = 0
                    new_node = node
                    for variable in variables:
                        init = inits[i]
                        src = variable['src']
                        i = i+1

                        new_statement = {'nodeType':'VariableDefinitionStatement',
                                         'src': src,
                                         'declarations':[variable],
                                         'initialValue':init}
                        new_node = self._parse_variable_definition(new_statement, new_node)

                else:
                    # If we have
                    # var (a, b) = f()
                    # we can split in multiple declarations, without init
                    # Then we craft one expression that does the assignment                   
                    variables = []
                    i = 0
                    new_node = node
                    for variable in statement['declarations']:
                        i = i+1
                        if variable:
                            src = variable['src']
                            # Create a fake statement to be consistent
                            new_statement = {'nodeType':'VariableDefinitionStatement',
                                             'src': src,
                                             'declarations':[variable]}
                            variables.append(variable)

                            new_node = self._parse_variable_definition_init_tuple(new_statement,
                                                                                  i,
                                                                                  new_node)

                    var_identifiers = []
                    # craft of the expression doing the assignement
                    for v in variables:
                        identifier = {
                            'nodeType':'Identifier',
                            'src': v['src'],
                            'name': v['name'],
                            'typeDescriptions': {
                                'typeString':v['typeDescriptions']['typeString']
                            }
                        }
                        var_identifiers.append(identifier)

                    tuple_expression = {'nodeType':'TupleExpression',
                                        'src': statement['src'],
                                        'components':var_identifiers}

                    expression = {
                        'nodeType' : 'Assignment',
                        'src':statement['src'],
                        'operator': '=',
                        'type':'tuple()',
                        'leftHandSide': tuple_expression,
                        'rightHandSide': statement['initialValue'],
                        'typeDescriptions': {'typeString':'tuple()'}
                        }
                    node = new_node
                    new_node = self._new_node(NodeType.EXPRESSION, statement['src'])
                    new_node.add_unparsed_expression(expression)
                    link_nodes(node, new_node)


            else:
                count = 0
                children = statement[self.get_children('children')]
                child = children[0]
                while child[self.get_key()] == 'VariableDeclaration':
                    count = count +1
                    child = children[count]

                assert len(children) == (count + 1)
                tuple_vars = children[count]


                variables_declaration = children[0:count]
                i = 0
                new_node = node
                if tuple_vars[self.get_key()] == 'TupleExpression':
                    assert len(tuple_vars[self.get_children('children')]) == count
                    for variable in variables_declaration:
                        init = tuple_vars[self.get_children('children')][i]
                        src = variable['src']
                        i = i+1
                        # Create a fake statement to be consistent
                        new_statement = {self.get_key():'VariableDefinitionStatement',
                                         'src': src,
                                         self.get_children('children'):[variable, init]}

                        new_node = self._parse_variable_definition(new_statement, new_node)
                else:
                    # If we have
                    # var (a, b) = f()
                    # we can split in multiple declarations, without init
                    # Then we craft one expression that does the assignment
                    assert tuple_vars[self.get_key()] in ['FunctionCall', 'Conditional']
                    variables = []
                    for variable in variables_declaration:
                        src = variable['src']
                        i = i+1
                        # Create a fake statement to be consistent
                        new_statement = {self.get_key():'VariableDefinitionStatement',
                                         'src': src,
                                         self.get_children('children'):[variable]}
                        variables.append(variable)

                        new_node = self._parse_variable_definition_init_tuple(new_statement, i, new_node)
                    var_identifiers = []
                    # craft of the expression doing the assignement
                    for v in variables:
                        identifier = {
                            self.get_key() : 'Identifier',
                            'src': v['src'],
                            'attributes': {
                                    'value': v['attributes'][self.get_key()],
                                    'type': v['attributes']['type']}
                        }
                        var_identifiers.append(identifier)

                    expression = {
                        self.get_key() : 'Assignment',
                        'src':statement['src'],
                        'attributes': {'operator': '=',
                                       'type':'tuple()'},
                        self.get_children('children'):
                        [{self.get_key(): 'TupleExpression',
                          'src': statement['src'],
                          self.get_children('children'): var_identifiers},
                         tuple_vars]}
                    node = new_node
                    new_node = self._new_node(NodeType.EXPRESSION, statement['src'])
                    new_node.add_unparsed_expression(expression)
                    link_nodes(node, new_node)


            return new_node