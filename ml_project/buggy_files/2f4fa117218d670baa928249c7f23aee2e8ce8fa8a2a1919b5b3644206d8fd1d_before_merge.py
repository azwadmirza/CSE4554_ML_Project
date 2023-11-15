    def _init_from_declaration(self, var, init):
        if self._is_compact_ast:
            attributes = var
            self._typeName = attributes['typeDescriptions']['typeString']
        else:
            assert len(var['children']) <= 2
            assert var['name'] == 'VariableDeclaration'

            attributes = var['attributes']
            self._typeName = attributes['type']

        self._name = attributes['name']
        self._arrayDepth = 0
        self._isMapping = False
        self._mappingFrom = None
        self._mappingTo = False
        self._initial_expression = None
        self._type = None

        if 'constant' in attributes:
            self._is_constant = attributes['constant']

        self._analyze_variable_attributes(attributes)

        if self._is_compact_ast:
            if var['typeName']:
                self._elem_to_parse = var['typeName']
            else:
                self._elem_to_parse = UnknownType(var['typeDescriptions']['typeString'])
        else:
            if not var['children']:
                # It happens on variable declared inside loop declaration
                try:
                    self._type = ElementaryType(self._typeName)
                    self._elem_to_parse = None
                except NonElementaryType:
                    self._elem_to_parse = UnknownType(self._typeName)
            else:
                self._elem_to_parse = var['children'][0]

        if self._is_compact_ast:
            self._initializedNotParsed = init
            if init:
                self._initialized = True
        else:
            if init: # there are two way to init a var local in the AST
                assert len(var['children']) <= 1
                self._initialized = True
                self._initializedNotParsed = init
            elif len(var['children']) in [0, 1]:
                self._initialized = False
                self._initializedNotParsed = []
            else:
                assert len(var['children']) == 2
                self._initialized = True
                self._initializedNotParsed = var['children'][1]