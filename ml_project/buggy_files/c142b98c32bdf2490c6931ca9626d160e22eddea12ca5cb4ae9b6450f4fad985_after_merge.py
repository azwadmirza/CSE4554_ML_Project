    def __call__(self, predicted_trees: List[Tree], gold_trees: List[Tree]) -> None:  # type: ignore
        """
        # Parameters

        predicted_trees : `List[Tree]`
            A list of predicted NLTK Trees to compute score for.
        gold_trees : `List[Tree]`
            A list of gold NLTK Trees to use as a reference.
        """
        if not os.path.exists(self._evalb_program_path):
            logger.warning(
                f"EVALB not found at {self._evalb_program_path}.  Attempting to compile it."
            )
            EvalbBracketingScorer.compile_evalb(self._evalb_directory_path)

            # If EVALB executable still doesn't exist, raise an error.
            if not os.path.exists(self._evalb_program_path):
                compile_command = (
                    f"python -c 'from allennlp.training.metrics import EvalbBracketingScorer; "
                    f'EvalbBracketingScorer.compile_evalb("{self._evalb_directory_path}")\''
                )
                raise ConfigurationError(
                    f"EVALB still not found at {self._evalb_program_path}. "
                    "You must compile the EVALB scorer before using it."
                    " Run 'make' in the '{}' directory or run: {}".format(
                        self._evalb_program_path, compile_command
                    )
                )
        tempdir = tempfile.mkdtemp()
        gold_path = os.path.join(tempdir, "gold.txt")
        predicted_path = os.path.join(tempdir, "predicted.txt")
        with open(gold_path, "w") as gold_file:
            for tree in gold_trees:
                gold_file.write(f"{tree.pformat(margin=1000000)}\n")

        with open(predicted_path, "w") as predicted_file:
            for tree in predicted_trees:
                predicted_file.write(f"{tree.pformat(margin=1000000)}\n")

        command = [
            self._evalb_program_path,
            "-p",
            self._evalb_param_path,
            "-e",
            str(self._evalb_num_errors_to_kill),
            gold_path,
            predicted_path,
        ]
        completed_process = subprocess.run(
            command, stdout=subprocess.PIPE, universal_newlines=True, check=True
        )

        _correct_predicted_brackets = 0.0
        _gold_brackets = 0.0
        _predicted_brackets = 0.0

        for line in completed_process.stdout.split("\n"):
            stripped = line.strip().split()
            if len(stripped) == 12 and stripped != self._header_line:
                # This line contains results for a single tree.
                numeric_line = [float(x) for x in stripped]
                _correct_predicted_brackets += numeric_line[5]
                _gold_brackets += numeric_line[6]
                _predicted_brackets += numeric_line[7]

        shutil.rmtree(tempdir)

        if is_distributed():
            device = torch.device("cuda" if dist.get_backend() == "nccl" else "cpu")
            correct_predicted_brackets = torch.tensor(_correct_predicted_brackets).to(device)
            predicted_brackets = torch.tensor(_predicted_brackets).to(device)
            gold_brackets = torch.tensor(_gold_brackets).to(device)
            dist.all_reduce(correct_predicted_brackets, op=dist.ReduceOp.SUM)
            dist.all_reduce(predicted_brackets, op=dist.ReduceOp.SUM)
            dist.all_reduce(gold_brackets, op=dist.ReduceOp.SUM)
            _correct_predicted_brackets = correct_predicted_brackets.item()
            _predicted_brackets = predicted_brackets.item()
            _gold_brackets = gold_brackets.item()

        self._correct_predicted_brackets += _correct_predicted_brackets
        self._gold_brackets += _gold_brackets
        self._predicted_brackets += _predicted_brackets