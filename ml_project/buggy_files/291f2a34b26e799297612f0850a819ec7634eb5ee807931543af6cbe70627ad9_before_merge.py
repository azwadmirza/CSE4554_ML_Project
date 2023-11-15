    def generate_text(
        self,
        prefix: str = "\n",
        number_of_characters: int = 1000,
        temperature: float = 1.0,
        break_on_suffix=None,
    ) -> Tuple[str, float]:

        if prefix == "":
            prefix = "\n"

        with torch.no_grad():
            characters = []

            idx2item = self.dictionary.idx2item

            # initial hidden state
            hidden = self.init_hidden(1)

            if len(prefix) > 1:

                char_tensors = []
                for character in prefix[:-1]:
                    char_tensors.append(
                        torch.tensor(self.dictionary.get_idx_for_item(character))
                        .unsqueeze(0)
                        .unsqueeze(0)
                    )

                input = torch.cat(char_tensors).to(flair.device)

                prediction, _, hidden = self.forward(input, hidden)

            input = (
                torch.tensor(self.dictionary.get_idx_for_item(prefix[-1]))
                .unsqueeze(0)
                .unsqueeze(0)
            )

            log_prob = 0.0

            for i in range(number_of_characters):

                input = input.to(flair.device)

                # get predicted weights
                prediction, _, hidden = self.forward(input, hidden)
                prediction = prediction.squeeze().detach()
                decoder_output = prediction

                # divide by temperature
                prediction = prediction.div(temperature)

                # to prevent overflow problem with small temperature values, substract largest value from all
                # this makes a vector in which the largest value is 0
                max = torch.max(prediction)
                prediction -= max

                # compute word weights with exponential function
                word_weights = prediction.exp().cpu()

                # try sampling multinomial distribution for next character
                try:
                    word_idx = torch.multinomial(word_weights, 1)[0]
                except:
                    word_idx = torch.tensor(0)

                # print(word_idx)
                prob = decoder_output[word_idx]
                log_prob += prob

                input = word_idx.detach().unsqueeze(0).unsqueeze(0)
                word = idx2item[word_idx].decode("UTF-8")
                characters.append(word)

                if break_on_suffix is not None:
                    if "".join(characters).endswith(break_on_suffix):
                        break

            text = prefix + "".join(characters)

            log_prob = log_prob.item()
            log_prob /= len(characters)

            if not self.is_forward_lm:
                text = text[::-1]

            text = text.encode("utf-8")

            return text, log_prob