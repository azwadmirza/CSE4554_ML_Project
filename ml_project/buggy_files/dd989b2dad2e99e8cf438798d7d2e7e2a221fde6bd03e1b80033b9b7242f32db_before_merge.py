    def measure_objects(self, workspace):
        image_set = workspace.image_set
        GT_img = image_set.get_image(self.img_obj_found_in_GT.value)
        ID_img = image_set.get_image(self.img_obj_found_in_ID.value)
        ID_pixels = ID_img.pixel_data
        GT_pixels = GT_img.pixel_data
        GT_pixels = ID_img.crop_image_similarly(GT_pixels)
        GT_mask = ID_img.crop_image_similarly(GT_img.mask)
        ID_mask = ID_img.mask
        mask  = GT_mask & ID_mask
        object_name_GT = self.object_name_GT.value
        objects_GT = workspace.get_objects(object_name_GT)
        iGT,jGT,lGT = objects_GT.ijv.transpose() 
        object_name_ID = self.object_name_ID.value
        objects_ID = workspace.get_objects(object_name_ID)
        iID, jID, lID = objects_ID.ijv.transpose()
        ID_obj = max(lID)
        GT_obj  = max(lGT)
        intersect_matrix = np.zeros((ID_obj, GT_obj))
        GT_tot_area = []
        all_intersect_area = []
        FN_area = np.zeros((ID_obj, GT_obj))

        xGT, yGT = np.shape(GT_pixels)
        xID, yID = np.shape(ID_pixels)
        GT_pixels = np.zeros((xGT, yGT))
        ID_pixels = np.zeros((xID, yID))
        total_pixels = xGT*yGT

        for ii in range(0, GT_obj):
            indices_ii = np.nonzero(lGT == ii)
            indices_ii = indices_ii[0]
            iGT_ii = iGT[indices_ii]
            jGT_ii = jGT[indices_ii]
            GT_set = set(zip(iGT_ii, jGT_ii))
            for jj in range(0, ID_obj):
                indices_jj = np.nonzero(lID==jj)
                indices_jj = indices_jj[0]
                iID_jj = iID[indices_jj]
                jID_jj = jID[indices_jj]
                ID_set = set(zip(iID_jj, jID_jj))
                area_overlap = len(GT_set & ID_set)
                all_intersect_area += [area_overlap]
                intersect_matrix[jj,ii] = area_overlap
                FN_area[jj,ii] = len(GT_set) - area_overlap
            GT_pixels[iGT, jGT] = 1    
            GT_tot_area += [len(GT_set)]

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
        GT_tot_area = np.sum(GT_tot_area)

        all_intersecting_area = np.sum(all_intersect_area)

        
        accuracy = TP/all_intersecting_area
        recall  = TP/GT_tot_area
        precision = TP/(TP+FP)
        F_factor = 2*(precision*recall)/(precision+recall)
        true_positive_rate = TP/(FN+TP)
        false_positive_rate = FP/(FP+TN)
        false_negative_rate = FN/(FN+TP)
        true_negative_rate = TN / (FP+TN)
        #
        # Temporary - assume not ijv
        #
        #rand_index, adjusted_rand_index = self.compute_rand_index_ijv(
        #    gt_ijv, objects_ijv, mask)
        #
        gt_labels = np.zeros(mask.shape, np.int64)
        gt_labels[iGT, jGT] = lGT
        test_labels = np.zeros(mask.shape, np.int64)
        test_labels[iID, jID] = lID
        rand_index, adjusted_rand_index = self.compute_rand_index_ijv(
            objects_GT.ijv, objects_ID.ijv, mask)
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