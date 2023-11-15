    def forward(self, state, x):
        if state is None:
            h = [to_device(self, self.zero_state(x.size(0))) for n in six.moves.range(self.n_layers)]
            state = {'h': h}
            if self.typ == "lstm":
                c = [to_device(self, self.zero_state(x.size(0))) for n in six.moves.range(self.n_layers)]
                state = {'c': c, 'h': h}

        h = [None] * self.n_layers
        emb = self.embed(x)
        if self.typ == "lstm":
            c = [None] * self.n_layers
            h[0], c[0] = self.rnn[0](self.dropout[0](emb), (state['h'][0], state['c'][0]))
            for n in six.moves.range(1, self.n_layers):
                h[n], c[n] = self.rnn[n](self.dropout[n](h[n - 1]), (state['h'][n], state['c'][n]))
            state = {'c': c, 'h': h}
        else:
            h[0] = self.rnn[0](self.dropout[0](emb), state['h'][0])
            for n in six.moves.range(1, self.n_layers):
                h[n] = self.rnn[n](self.dropout[n](h[n - 1]), state['h'][n])
            state = {'h': h}
        y = self.lo(self.dropout[-1](h[-1]))
        return state, y