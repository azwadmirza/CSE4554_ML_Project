  def _make_eval_prediction_hooks_fn(self):
    external_scorers = self._config["eval"].get("external_evaluators")
    if not self._config["eval"].get("save_eval_predictions", False) and external_scorers is None:
      return None
    if self._model.unsupervised:
      raise RuntimeError("This model does not support saving evaluation predictions")
    save_path = os.path.join(self._config["model_dir"], "eval")
    if not tf.gfile.Exists(save_path):
      tf.gfile.MakeDirs(save_path)
    if external_scorers is not None:
      external_evaluator = evaluator.ExternalEvaluator(
          labels_file=self._config["data"]["eval_labels_file"],
          output_dir=save_path,
          scorers=evaluator.make_scorers(external_scorers))
    else:
      external_evaluator = None
    return lambda predictions: [
        hooks.SaveEvaluationPredictionHook(
            self._model,
            os.path.join(save_path, "predictions.txt"),
            post_evaluation_fn=external_evaluator,
            predictions=predictions)]