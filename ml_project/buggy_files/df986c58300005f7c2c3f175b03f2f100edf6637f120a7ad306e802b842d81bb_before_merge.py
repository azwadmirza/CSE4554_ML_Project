    def eval(self, model):
        """
        Performs evaluation on a given model.

        :param model: The model on which to perform evaluation
        :type model: AdaptiveModel
        :return all_results: A list of dictionaries, one for each prediction head. Each dictionary contains the metrics
                             and reports generated during evaluation.
        :rtype all_results: list of dicts
        """
        model.eval()

        # init empty lists per prediction head
        loss_all = [0 for _ in model.prediction_heads]
        preds_all = [[] for _ in model.prediction_heads]
        label_all = [[] for _ in model.prediction_heads]

        for step, batch in enumerate(
            tqdm(self.data_loader, desc="Evaluating", mininterval=10)
        ):
            batch = {key: batch[key].to(self.device) for key in batch}

            with torch.no_grad():

                logits = model.forward(**batch)
                # TODO logits_to_loss should be a single, overloaded function
                losses_per_head = model.logits_to_loss_per_head(logits=logits, **batch)
                preds = model.logits_to_preds(
                    logits=logits, **batch
                )

                labels = model.prepare_labels(**batch)

            # stack results of all batches per prediction head
            for head_num, head in enumerate(model.prediction_heads):
                loss_all[head_num] += np.sum(to_numpy(losses_per_head[head_num]))
                preds_all[head_num] += list(to_numpy(preds[head_num]))
                label_all[head_num] += list(to_numpy(labels[head_num]))


        # Evaluate per prediction head
        all_results = []
        for head_num, head in enumerate(model.prediction_heads):
            if head.model_type == "multilabel_text_classification":
                # converting from string preds back to multi-hot encoding
                from sklearn.preprocessing import MultiLabelBinarizer
                mlb = MultiLabelBinarizer(classes=head.label_list)
                preds_all[head_num] = mlb.fit_transform(preds_all[head_num])
                label_all[head_num] = mlb.transform(label_all[head_num])

            result = {"loss": loss_all[head_num] / len(self.data_loader.dataset),
                      "task_name": head.task_name}
            result.update(
                compute_metrics(metric=head.metric, preds=preds_all[head_num], labels=label_all[head_num]
                )
            )

            # Select type of report depending on prediction head output type
            if self.classification_report:
                if head.ph_output_type == "per_token":
                    report_fn = token_classification_report
                elif head.ph_output_type == "per_sequence":
                    report_fn = classification_report
                elif head.ph_output_type == "per_token_squad":
                    report_fn = lambda *args, **kwargs: "not Implemented"
                elif head.ph_output_type == "per_sequence_continuous":
                    report_fn = r2_score
                else:
                    raise NotImplementedError

                # CHANGE PARAMETERS, not all report_fn accept digits
                if head.ph_output_type == "per_sequence_continuous":
                    result["report"] = report_fn(
                        label_all[head_num], preds_all[head_num]
                    )
                elif head.ph_output_type == "per_token":
                    result["report"] = report_fn(
                        label_all[head_num], preds_all[head_num]
                    )
                else:
                    # supply labels as all possible combination because if ground truth labels do not cover
                    # all values in label_list (maybe dev set is small), the report will break
                    result["report"] = report_fn(
                        label_all[head_num],
                        preds_all[head_num],
                        digits=4,
                        target_names=head.label_list)

            all_results.append(result)

        return all_results