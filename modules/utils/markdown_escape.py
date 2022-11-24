import re
escape_chars = r'_[]()~*`>#+-=|{}.!'

def escape(text):
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)