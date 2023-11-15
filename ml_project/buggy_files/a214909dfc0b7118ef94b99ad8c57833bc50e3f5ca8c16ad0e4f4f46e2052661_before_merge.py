async def parse_regex(opsdroid, skills, message):
    """Parse a message against all regex skills."""
    matched_skills = []
    for skill in skills:
        for matcher in skill.matchers:
            if "regex" in matcher:
                opts = matcher["regex"]
                if opts["case_sensitive"]:
                    regex = re.search(opts["expression"],
                                      message.text)
                else:
                    regex = re.search(opts["expression"],
                                      message.text, re.IGNORECASE)
                if regex:
                    message.regex = regex
                    matched_skills.append({
                        "score": await calculate_score(
                            opts["expression"], opts["score_factor"]),
                        "skill": skill,
                        "config": skill.config,
                        "message": message
                    })
    return matched_skills