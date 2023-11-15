    def stem(self, word):
        """
         Stem an Arabic word and return the stemmed form.
        :param word: string
        :return: string
        """
        # set initial values
        self.is_verb = True
        self.is_noun = True
        self.is_defined = False

        self.suffix_verb_step2a_success = False
        self.suffix_verb_step2b_success = False
        self.suffix_noun_step2c2_success = False
        self.suffix_noun_step1a_success = False
        self.suffix_noun_step2a_success = False
        self.suffix_noun_step2b_success = False
        self.suffixe_noun_step1b_success = False
        self.prefix_step2a_success = False
        self.prefix_step3a_noun_success = False
        self.prefix_step3b_noun_success = False

        modified_word = word
        # guess type and properties
        # checks1
        self.__checks_1(modified_word)
        # checks2
        self.__checks_2(modified_word)
        modified_word = self.__normalize_pre(modified_word)
        if self.is_verb:
            modified_word = self.__Suffix_Verb_Step1(modified_word)
            if  self.suffixes_verb_step1_success:
                modified_word = self.__Suffix_Verb_Step2a(modified_word)
                if not self.suffix_verb_step2a_success :
                    modified_word = self.__Suffix_Verb_Step2c(modified_word)
                #or next
            else:
                modified_word = self.__Suffix_Verb_Step2b(modified_word)
                if not self.suffix_verb_step2b_success:
                    modified_word = self.__Suffix_Verb_Step2a(modified_word)
        if self.is_noun:
            modified_word = self.__Suffix_Noun_Step2c2(modified_word)
            if not self.suffix_noun_step2c2_success:
                if not self.is_defined:
                    modified_word = self.__Suffix_Noun_Step1a(modified_word)
                    #if self.suffix_noun_step1a_success:
                    modified_word = self.__Suffix_Noun_Step2a(modified_word)
                    if not self.suffix_noun_step2a_success:
                        modified_word = self.__Suffix_Noun_Step2b(modified_word)
                    if not self.suffix_noun_step2b_success and not self.suffix_noun_step2a_success:
                        modified_word = self.__Suffix_Noun_Step2c1(modified_word)
                    # or next ? todo : how to deal with or next
                else:
                    modified_word =  self.__Suffix_Noun_Step1b(modified_word)
                    if self.suffixe_noun_step1b_success:
                        modified_word = self.__Suffix_Noun_Step2a(modified_word)
                        if not self.suffix_noun_step2a_success:
                            modified_word = self.__Suffix_Noun_Step2b(modified_word)
                        if not self.suffix_noun_step2b_success and not self.suffix_noun_step2a_success:
                            modified_word = self.__Suffix_Noun_Step2c1(modified_word)
                    else:
                        if not self.is_defined:
                            modified_word = self.__Suffix_Noun_Step2a(modified_word)
                        modified_word = self.__Suffix_Noun_Step2b(modified_word)
            modified_word = self.__Suffix_Noun_Step3(modified_word)
        if not self.is_noun and self.is_verb:
            modified_word = self.__Suffix_All_alef_maqsura(modified_word)

        # prefixes
        modified_word = self.__Prefix_Step1(modified_word)
        modified_word = self.__Prefix_Step2a(modified_word)
        if not self.prefix_step2a_success:
            modified_word = self.__Prefix_Step2b(modified_word)
        modified_word = self.__Prefix_Step3a_Noun(modified_word)
        if not self.prefix_step3a_noun_success and self.is_noun:
            modified_word = self.__Prefix_Step3b_Noun(modified_word)
        else:
            if not self.prefix_step3b_noun_success and self.is_verb:
                modified_word = self.__Prefix_Step3_Verb(modified_word)
                modified_word = self.__Prefix_Step4_Verb(modified_word)

        # post normalization stemming
        modified_word = self.__normalize_post(modified_word)
        stemmed_word = modified_word
        return stemmed_word