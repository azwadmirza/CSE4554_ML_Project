    def get_html_tree(self):
        self.html = "<html>"
        for page_num in self.elems.keys():
            page_html = "<div id=" + str(page_num) + ">"
            boxes = []
            for clust in self.tree[page_num]:
                for (pnum, pwidth, pheight, top, left, bottom, right) in self.tree[page_num][clust]:
                    boxes += [[clust.lower().replace(' ', '_'), top, left,
                               bottom, right]]

            # TODO: We need to detect columns and sort acccordingly.
            boxes.sort(key=cmp_to_key(column_order))

            #  from pprint import pprint
            #  pprint(boxes, width=120)
            #  import pdb; pdb.set_trace()

            for box in boxes:
                if(box[0] == "table"):
                    table = box[1:]
                    table_html = self.get_html_table(table, page_num)
                    if six.PY2:
                        page_html += table_html.decode('utf-8')
                    elif six.PY3:
                        page_html += table_html
                elif(box[0] == "figure"):
                    fig_str = [str(i) for i in box[1:]]
                    fig_html = ("<figure bbox=" + ",".join(fig_str) +
                                "></figure>")
                    if six.PY2:
                        page_html += fig_html.decode('utf-8')
                    elif six.PY3:
                        page_html += fig_html
                else:
                    (box_html, char_html, top_html, left_html, bottom_html,
                     right_html) = self.get_html_others(box[1:], page_num)
                    page_html += ("<" + box[0] + " char='" + char_html +
                                  "', top='" + top_html + "', left='" +
                                  left_html + "', bottom='" + bottom_html +
                                  "', right='" + right_html + "'>" + box_html +
                                  "</" + box[0] + ">")
            page_html += "</div>"
            self.html += page_html
        self.html += "</html>"
        return self.html