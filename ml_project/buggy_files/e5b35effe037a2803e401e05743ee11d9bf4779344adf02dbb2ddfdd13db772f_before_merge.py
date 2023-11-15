    def __init__(self, filename, filename_info, filetype_info):
        """Initialize the reader."""
        super(HRITJMAFileHandler, self).__init__(filename, filename_info,
                                                 filetype_info,
                                                 (jma_hdr_map,
                                                  jma_variable_length_headers,
                                                  jma_text_headers))

        self.mda['segment_sequence_number'] = self.mda['image_segm_seq_no']
        self.mda['planned_end_segment_number'] = self.mda['total_no_image_segm']
        self.mda['planned_start_segment_number'] = 1

        items = self.mda['image_data_function'].split('\r')
        if items[0].startswith('$HALFTONE'):
            self.calibration_table = []
            for item in items[1:]:
                if item == '':
                    continue
                key, value = item.split(':=')
                if key.startswith('_UNIT'):
                    self.mda['unit'] = item.split(':=')[1]
                elif key.startswith('_NAME'):
                    pass
                elif key.isdigit():
                    key = int(key)
                    value = float(value)
                    self.calibration_table.append((key, value))

            self.calibration_table = np.array(self.calibration_table)

        sublon = float(self.mda['projection_name'].strip().split('(')[1][:-1])
        self.mda['projection_parameters']['SSP_longitude'] = sublon