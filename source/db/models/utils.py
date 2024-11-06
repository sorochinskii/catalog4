

def split_and_concatenate(string: str) -> str:

    words = []
    prev = ''
    rev_string = string[::-1]
    temp = ''
    for i, letter in enumerate(rev_string):
        if i + 1 == len(string):
            temp += letter
            words.append(temp)
        elif not prev:
            temp += letter
        elif letter.islower() and prev.islower():
            temp += letter
        elif letter.isupper() and prev.islower():
            temp += letter
            words.append(temp)
            temp = ''
            prev = ''
            continue
        elif letter.islower() and prev.isupper():
            words.append(temp)
            temp = ''
            temp += letter
        elif letter.isupper() and prev.isupper():
            temp += letter
        prev = letter
    result = "_".join(words).lower()[::-1]
    return result


assert split_and_concatenate('MFPNetwork') == 'mfp_network'
assert split_and_concatenate('MFP') == 'mfp'
assert split_and_concatenate('AAbCD') == 'a_ab_cd'
assert split_and_concatenate('AbBCd') == 'ab_b_cd'
assert split_and_concatenate('ABCdDDD') == 'ab_cd_ddd'
