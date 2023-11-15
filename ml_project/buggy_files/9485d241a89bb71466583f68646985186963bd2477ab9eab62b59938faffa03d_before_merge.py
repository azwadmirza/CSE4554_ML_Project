    def measure_objects(self, workspace):
        image_set = workspace.image_set
        object_name_GT = self.object_name_GT.value
        objects_GT = workspace.get_objects(object_name_GT)
        iGT,jGT,lGT = objects_GT.ijv.transpose() 
        object_name_ID = self.object_name_ID.value
        objects_ID = workspace.get_objects(object_name_ID)
        iID, jID, lID = objects_ID.ijv.transpose()
        ID_obj = 0 if len(lID) == 0 else max(lID)
        GT_obj  = 0 if len(lGT) == 0 else max(lGT)

        xGT, yGT = objects_GT.shape
        xID, yID = objects_ID.shape
        GT_pixels = np.zeros((xGT, yGT))
        ID_pixels = np.zeros((xID, yID))
        total_pixels = xGT*yGT

        GT_pixels[iGT, jGT] = 1
        ID_pixels[iID, jID] = 1

        GT_tot_area = len(iGT)
        if len(iGT) == 0 and len(iID) == 0:
            intersect_matrix = np.zeros((0, 0), int)
        else:
            #
            # Build a matrix with rows of i, j, label and a GT/ID flag
            #
            all_ijv = np.column_stack(
                (np.hstack((iGT, iID)),
                 np.hstack((jGT, jID)),
                 np.hstack((lGT, lID)),
                 np.hstack((np.zeros(len(iGT)), np.ones(len(iID))))))
            #
            # Order it so that runs of the same i, j are consecutive
            #
            order = np.lexsort((all_ijv[:, -1], all_ijv[:, 0], all_ijv[:, 1]))
            all_ijv = all_ijv[order, :]
            # Mark the first at each i, j != previous i, j
            first = np.where(np.hstack(
                ([True], 
                 ~ np.all(all_ijv[:-1, :2] == all_ijv[1:, :2], 1), 
                 [True])))[0]
            # Count # at each i, j
            count = first[1:] - first[:-1]
            # First indexer - mapping from i,j to index in all_ijv
            all_ijv_map = Indexes([count])
            # Bincount to get the # of ID pixels per i,j
            id_count = np.bincount(all_ijv_map.rev_idx,
                                   all_ijv[:, -1]).astype(int)
            gt_count = count - id_count
            # Now we can create an indexer that has NxM elements per i,j
            # where N is the number of GT pixels at that i,j and M is
            # the number of ID pixels. We can then use the indexer to pull
            # out the label values for each to populate a sparse array.
            #
            cross_map = Indexes([id_count, gt_count])
            off_gt = all_ijv_map.fwd_idx[cross_map.rev_idx] + cross_map.idx[0]
            off_id = all_ijv_map.fwd_idx[cross_map.rev_idx] + cross_map.idx[1]+\
                id_count[cross_map.rev_idx]
            intersect_matrix = coo_matrix(
                (np.ones(len(off_gt)), 
                 (all_ijv[off_id, 2], all_ijv[off_gt, 2])),
                shape = (ID_obj+1, GT_obj+1)).toarray()[1:, 1:]
        
        gt_areas = objects_GT.areas
        FN_area = gt_areas[np.newaxis, :] - intersect_matrix
        all_intersecting_area = np.sum(intersect_matrix)
        
        dom_ID = []

        for i in range(0, ID_obj):
            indices_jj = np.nonzero(lID==i)
            indices_jj = indices_jj[0]
            id_i = iID[indices_jj]
            id_j = jID[indices_jj]
            ID_pixels[id_i, id_j] = 1

        for i in intersect_matrix:  # loop through the GT objects first                                
            if max(i) == 0:
                id = -1  # we missed the object; arbitrarily assign -1 index                                                          
            else:
                id = np.where(i == max(i))[0][0] # what is the ID of the max pixels?                                                            
            dom_ID += [id]  # for ea GT object, which is the dominating ID?                                                                    

        dom_ID = np.array(dom_ID)
        
        for i in range(0, len(intersect_matrix.T)):
            if len(np.where(dom_ID == i)[0]) > 1:
                final_id = np.where(intersect_matrix.T[i] == max(intersect_matrix.T[i]))
                final_id = final_id[0][0]
                all_id = np.where(dom_ID == i)[0]
                nonfinal = [x for x in all_id if x != final_id]
                for n in nonfinal:  # these others cannot be candidates for the corr ID now                                                      
                    intersect_matrix.T[i][n] = 0
            else :
                continue

        TP = []
        TN = []
        FN = []
        for i in range(0,len(dom_ID)):
            d = dom_ID[i]
            tp = intersect_matrix[i][d]
            TP += [tp]
            tp = intersect_matrix[i][d]
            fn = FN_area[i][d]
            tn = total_pixels - tp
            TP += [tp]
            TN += [tn]
            FN += [fn]

        FP = []
        for i in range(0,len(dom_ID)):
            d = dom_ID[i]
            fp = np.sum(intersect_matrix[i][0:d])+np.sum(intersect_matrix[i][(d+1)::])
            FP += [fp]
            d = dom_ID[i]
   
        FN = np.sum(FN)
        TN = np.sum(TN)
        TP = np.sum(TP)
        FP = np.sum(FP)

        accuracy = TP/all_intersecting_area
        recall  = TP/GT_tot_area
        precision = TP/(TP+FP)
        F_factor = 2*(precision*recall)/(precision+recall)
        true_positive_rate = TP/(FN+TP)
        false_positive_rate = FP/(FP+TN)
        false_negative_rate = FN/(FN+TP)
        true_negative_rate = TN / (FP+TN)
        shape = np.maximum(np.maximum(
            np.array(objects_GT.shape), np.array(objects_ID.shape)),
                           np.ones(2, int))
        rand_index, adjusted_rand_index = self.compute_rand_index_ijv(
            objects_GT.ijv, objects_ID.ijv, shape)
        m = workspace.measurements
        m.add_image_measurement(self.measurement_name(FTR_F_FACTOR), F_factor)
        m.add_image_measurement(self.measurement_name(FTR_PRECISION),
                                precision)
        m.add_image_measurement(self.measurement_name(FTR_RECALL), recall)
        m.add_image_measurement(self.measurement_name(FTR_TRUE_POS_RATE),
                                true_positive_rate)
        m.add_image_measurement(self.measurement_name(FTR_FALSE_POS_RATE),
                                false_positive_rate)
        m.add_image_measurement(self.measurement_name(FTR_TRUE_NEG_RATE),
                                true_negative_rate)
        m.add_image_measurement(self.measurement_name(FTR_FALSE_NEG_RATE),
                                false_negative_rate)
        m.add_image_measurement(self.measurement_name(FTR_RAND_INDEX),
                                rand_index)
        m.add_image_measurement(self.measurement_name(FTR_ADJUSTED_RAND_INDEX),
                                adjusted_rand_index)
        def subscripts(condition1, condition2):
            x1,y1 = np.where(GT_pixels == condition1)
            x2,y2 = np.where(ID_pixels == condition2)
            mask = set(zip(x1,y1)) & set(zip(x2,y2))
            return list(mask)

        TP_mask = subscripts(1,1)
        FN_mask = subscripts(1,0)
        FP_mask = subscripts(0,1)
        TN_mask = subscripts(0,0)

        TP_pixels = np.zeros((xGT,yGT))
        FN_pixels = np.zeros((xGT,yGT))
        FP_pixels = np.zeros((xGT,yGT))
        TN_pixels = np.zeros((xGT,yGT))

        def maskimg(mask,img):
            for ea in mask:
                img[ea] = 1
            return img

        TP_pixels = maskimg(TP_mask, TP_pixels)
        FN_pixels = maskimg(FN_mask, FN_pixels)
        FP_pixels = maskimg(FP_mask, FP_pixels)
        TN_pixels = maskimg(TN_mask, TN_pixels)

        if self.show_window:
            workspace.display_data.true_positives = TP_pixels
            workspace.display_data.true_negatives = FN_pixels
            workspace.display_data.false_positives = FP_pixels
            workspace.display_data.false_negatives = TN_pixels
            workspace.display_data.statistics = [
                (FTR_F_FACTOR, F_factor),
                (FTR_PRECISION, precision),
                (FTR_RECALL, recall),
                (FTR_FALSE_POS_RATE, false_positive_rate),
                (FTR_FALSE_NEG_RATE, false_negative_rate),
                (FTR_RAND_INDEX, rand_index),
                (FTR_ADJUSTED_RAND_INDEX, adjusted_rand_index)
            ]