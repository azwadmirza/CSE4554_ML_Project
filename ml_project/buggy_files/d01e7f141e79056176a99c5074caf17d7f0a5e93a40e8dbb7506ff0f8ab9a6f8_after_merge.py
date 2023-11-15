    def create_neg(self, neg_head):
        if neg_head:
            def fn(heads, relations, tails, num_chunks, chunk_size, neg_sample_size):
                hidden_dim = heads.shape[1]
                emb_real, emb_img = nd.split(tails, num_outputs=2, axis=-1)
                rel_real, rel_img = nd.split(relations, num_outputs=2, axis=-1)
                real = emb_real * rel_real + emb_img * rel_img
                img = -emb_real * rel_img + emb_img * rel_real
                emb_complex = nd.concat(real, img, dim=-1)
                tmp = emb_complex.reshape(num_chunks, chunk_size, hidden_dim)
                heads = heads.reshape(num_chunks, neg_sample_size, hidden_dim)
                heads = nd.transpose(heads, axes=(0, 2, 1))
                return nd.linalg_gemm2(tmp, heads)
            return fn
        else:
            def fn(heads, relations, tails, num_chunks, chunk_size, neg_sample_size):
                hidden_dim = heads.shape[1]
                emb_real, emb_img = nd.split(heads, num_outputs=2, axis=-1)
                rel_real, rel_img = nd.split(relations, num_outputs=2, axis=-1)
                real = emb_real * rel_real - emb_img * rel_img
                img = emb_real * rel_img + emb_img * rel_real
                emb_complex = nd.concat(real, img, dim=-1)
                tmp = emb_complex.reshape(num_chunks, chunk_size, hidden_dim)

                tails = tails.reshape(num_chunks, neg_sample_size, hidden_dim)
                tails = nd.transpose(tails, axes=(0, 2, 1))
                return nd.linalg_gemm2(tmp, tails)
            return fn