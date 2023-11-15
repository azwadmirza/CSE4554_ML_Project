    def get_candidates_and_features_page_num(self, page_num):
        elems = self.elems[page_num]
        #  font_stat = self.font_stats[page_num]
        #  lines_bboxes = self.get_candidates_lines(page_num, elems)
        alignments_bboxes, alignment_features = self.get_candidates_alignments(
            page_num, elems)
        # print "Page Num: ", page_num, "Line bboxes: ", len(lines_bboxes), ", Alignment bboxes: ", len(alignments_bboxes)
        # alignment_features += get_alignment_features(lines_bboxes, elems, font_stat)
        boxes = alignments_bboxes  # + lines_bboxes
        if len(boxes) == 0:
            return [], []
        lines_features = get_lines_features(boxes, elems)
        features = np.concatenate((np.array(alignment_features),
                                   np.array(lines_features)), axis=1)
        return boxes, features