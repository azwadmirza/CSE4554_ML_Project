    def __init__(self, var):
        '''
            A variable can be declared through a statement, or directly.
            If it is through a statement, the following children may contain
            the init value.
            It may be possible that the variable is declared through a statement,
            but the init value is declared at the VariableDeclaration children level
        '''

        super(VariableDeclarationSolc, self).__init__()
        self._was_analyzed = False
        self._elem_to_parse = None
        self._initializedNotParsed = None

        self._is_compact_ast = False

        if 'nodeType' in var:
            self._is_compact_ast = True
            nodeType = var['nodeType']
            if nodeType in ['VariableDeclarationStatement', 'VariableDefinitionStatement']:
                if len(var['declarations'])>1:
                    raise MultipleVariablesDeclaration
                init = None
                if 'initialValue' in var:
                    init = var['initialValue']
                self._init_from_declaration(var['declarations'][0], init)
            elif  nodeType == 'VariableDeclaration':
                self._init_from_declaration(var, var['value'])
            else:
                logger.error('Incorrect variable declaration type {}'.format(nodeType))
                exit(-1)

        else:
            nodeType = var['name']

            if nodeType in ['VariableDeclarationStatement', 'VariableDefinitionStatement']:
                if len(var['children']) == 2:
                    init = var['children'][1]
                elif len(var['children']) == 1:
                    init = None
                elif len(var['children']) > 2:
                    raise MultipleVariablesDeclaration
                else:
                    logger.error('Variable declaration without children?'+var)
                    exit(-1)
                declaration = var['children'][0]
                self._init_from_declaration(declaration, init)
            elif  nodeType == 'VariableDeclaration':
                self._init_from_declaration(var, None)
            else:
                logger.error('Incorrect variable declaration type {}'.format(nodeType))
                exit(-1)