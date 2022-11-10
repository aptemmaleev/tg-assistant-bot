def add_char(letter: str, n: int):
    c = ord(letter) - 65 + n
    if (c > 25):
        return(chr(c // 26 + 65 - 1) + chr(c % 26 + 65))
    else:
        return(chr(c % 26 + 65))
    