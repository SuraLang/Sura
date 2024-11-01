import re

class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {self.value})"

# Define tokens and patterns
TOKENS = {
    'KEYWORDS': ["תניא", "בעא_מיניה", "אמר_ליה", "הדרן_עלך", "אי", "אי_נמי", "אידך", "אין", "לא"],
    'OPERATORS': ["﬩=", "+=", "-=", "*=", "/=", "%=", "﬩﬩", "++", "--", "==", "!=", ">=", "<=", ">", "<", "&&", "||", "﬩", "+", "-", "*", "/", "%", "="],
    'DELIMITERS': ["{", "}", "(", ")", "[", "]", ",", ";"]
}

TOKEN_PATTERNS = [
    ('KEYWORD', r'\b(?:' + '|'.join(TOKENS['KEYWORDS']) + r')\b'),
    ('NUMBER', r'\b\d+\b'),
    ('STRING', r'"[^"]*"'),
    ('OPERATOR', r'|'.join(re.escape(op) for op in TOKENS['OPERATORS'])),
    ('DELIMITER', r'|'.join(re.escape(delim) for delim in TOKENS['DELIMITERS'])),
    ('IDENTIFIER', r'\b\w+\b'),
    ('WHITESPACE', r'\s+'),
    ('COMMENT_SINGLE', r'\\.*')
]

# Compile patterns
combined_pattern = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_PATTERNS)
compiled_pattern = re.compile(combined_pattern)

# Lexer function
def lexer(code):
    tokens = []
    for match in compiled_pattern.finditer(code):
        token_type = match.lastgroup
        value = match.group(token_type)
        
        if token_type in ('WHITESPACE', 'COMMENT_SINGLE'):
            continue  # Skip whitespace tokens
        
        if token_type == 'STRING':
            value = value[1:-1]  # Remove surrounding quotes

        tokens.append(Token(token_type, value))
    
    return tokens