    def _word_cloud(self, *, ids: torch.LongTensor, id_to_label: Mapping[int, str], top: int):
        try:
            from word_cloud.word_cloud_generator import WordCloud
        except ImportError:
            logger.warning(
                'Could not import module `word_cloud`. '
                'Try installing it with `pip install git+https://github.com/kavgan/word_cloud.git`',
            )
            return

        # pre-filter to keep only topk
        uniq, counts = ids.view(-1).unique(return_counts=True)
        top_counts, top_ids = counts.topk(k=top, largest=True)

        # generate text
        text = list(itertools.chain(*(
            itertools.repeat(id_to_label[e_id], count)
            for e_id, count in zip(top_ids.tolist(), top_counts.tolist())
        )))

        from IPython.core.display import HTML
        word_cloud = WordCloud()
        return HTML(word_cloud.get_embed_code(text=text, topn=top))