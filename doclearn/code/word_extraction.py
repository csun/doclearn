def identifier_to_words(identifier):
    """Returns a list of words contained by an identifier."""
    identifier = identifier.strip('_')

    if not identifier:
        return []

    lowered = identifier.lower()

    split = lowered.split('_')
    if len(split) > 1:
        return split

    index = 1
    next_split_start = 0
    words = []

    while index < len(identifier):
        if identifier[index] != lowered[index]:
            words.append(lowered[next_split_start:index])
            next_split_start = index
        index += 1

    words.append(lowered[next_split_start:index])
    return words
