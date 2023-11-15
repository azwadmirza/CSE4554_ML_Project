    def get_mouse_idx(self, event):
        '''Return the line index at the event's mouse coordinate'''
        x, y = event.GetPositionTuple()
        line_height = self.line_height + self.leading
        idx = int(y / line_height) + self.GetScrollPos(wx.SB_VERTICAL)
        idx = max(0, min(len(self)-1, idx))
        if y < line_height:
            # It's the slightly bogus directory at the top
            self.recalc()
            folder_idx = bisect.bisect_right(self.folder_idxs, idx)-1
            if folder_idx == -1:
                return -1
            idx = self.folder_idxs[folder_idx]
        return idx