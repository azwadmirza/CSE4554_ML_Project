    def edge_func(self, edges):
        real_head, img_head = nd.split(edges.src['emb'], num_outputs=2, axis=-1)
        real_tail, img_tail = nd.split(edges.dst['emb'], num_outputs=2, axis=-1)
        real_rel, img_rel = nd.split(edges.data['emb'], num_outputs=2, axis=-1)

        score = real_head * real_tail * real_rel \
                + img_head * img_tail * real_rel \
                + real_head * img_tail * img_rel \
                - img_head * real_tail * img_rel
        # TODO: check if there exists minus sign and if gamma should be used here(jin)
        return {'score': nd.sum(score, -1)}