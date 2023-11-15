    def _initialize(self):
        matrix_existed = self.effective_matrix is not None
        effective_matrix = self.effective_matrix
        self.__invalidated = True
        self.data = None
        self.effective_matrix = None
        self.closeContext()
        self.clear_messages()

        # if no data nor matrix is present reset plot
        if self.signal_data is None and self.matrix is None:
            self.clear()
            self.init_attr_values()
            return

        if self.signal_data is not None and self.matrix is not None and \
                len(self.signal_data) != len(self.matrix):
            self.Error.mismatching_dimensions()
            self.clear()
            self.init_attr_values()
            return

        if self.signal_data is not None:
            self.data = self.signal_data
        elif self.matrix_data is not None:
            self.data = self.matrix_data

        if self.matrix is not None:
            self.effective_matrix = self.matrix
            if self.matrix.axis == 0 and self.data is not None \
                    and self.data is self.matrix_data:
                names = [[attr.name] for attr in self.data.domain.attributes]
                domain = Domain([], metas=[StringVariable("labels")])
                self.data = Table(domain, names)
        elif self.data.domain.attributes:
            preprocessed_data = MDS().preprocess(self.data)
            self.effective_matrix = Euclidean(preprocessed_data)
        else:
            self.Error.no_attributes()
            self.clear()
            self.init_attr_values()
            return

        self.init_attr_values()
        self.openContext(self.data)
        self.__invalidated = not (matrix_existed and
                                  self.effective_matrix is not None and
                                  np.array_equal(effective_matrix,
                                                 self.effective_matrix))
        if self.__invalidated:
            self.clear()
        self.graph.set_effective_matrix(self.effective_matrix)