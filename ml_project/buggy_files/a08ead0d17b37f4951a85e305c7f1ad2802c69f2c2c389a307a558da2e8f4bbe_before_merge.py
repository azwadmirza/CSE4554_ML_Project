    def _load_relations(self):
        """Load relations from the train data and build vocab."""
        vocab = {}
        index2word = []
        all_relations = []  # List of all relation pairs
        node_relations = defaultdict(set)  # Mapping from node index to its related node indices

        logger.info("Loading relations from train data..")
        for relation in self.train_data:
            if len(relation) != 2:
                raise ValueError('Relation pair "%s" should have exactly two items' % repr(relation))
            for item in relation:
                if item in vocab:
                    vocab[item].count += 1
                else:
                    vocab[item] = Vocab(count=1, index=len(index2word))
                    index2word.append(item)
            node_1, node_2 = relation
            node_1_index, node_2_index = vocab[node_1].index, vocab[node_2].index
            node_relations[node_1_index].add(node_2_index)
            relation = (node_1_index, node_2_index)
            all_relations.append(relation)
        logger.info("Loaded %d relations from train data, %d nodes", len(all_relations), len(vocab))
        self.kv.vocab = vocab
        self.kv.index2word = index2word
        self.indices_set = set((range(len(index2word))))  # Set of all node indices
        self.indices_array = np.array(range(len(index2word)))  # Numpy array of all node indices
        counts = np.array([self.kv.vocab[index2word[i]].count for i in range(len(index2word))], dtype=np.float64)
        self._node_probabilities = counts / counts.sum()
        self._node_probabilities_cumsum = np.cumsum(self._node_probabilities)
        self.all_relations = all_relations
        self.node_relations = node_relations
        self._negatives_buffer = NegativesBuffer([])  # Buffer for negative samples, to reduce calls to sampling method
        self._negatives_buffer_size = 2000