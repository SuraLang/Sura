class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def parse(self):
        statements = []
        while self.position < len(self.tokens):
            statement = self.parse_statement()
            if statement:
                statements.append(statement)
        return statements

    def parse_statement(self):
        token = self.current_token()
    
        if token.type == 'KEYWORD':
            if token.value == 'אמר_ליה':
                self.advance()
                self.expect('DELIMITER', '(')
                expr = self.parse_expression()
                self.expect('DELIMITER', ')')
                return ('PRINT', expr)
    
            elif token.value == 'תניא':
                self.advance()
                var_name = self.expect('IDENTIFIER')
                self.expect('OPERATOR', '=')
                expr = self.parse_expression()
                return ('VAR_ASSIGN', var_name, expr)
    
            elif token.value == 'אי':  # תנאי if
                self.advance()
                self.expect('DELIMITER', '(')
                condition = self.parse_expression()
                self.expect('DELIMITER', ')')
                self.expect('DELIMITER', '{')
                true_branch = self.parse_block()
                branches = [('IF', condition, true_branch)]
    
                # טיפול במספר בלוקים של אי_נמי ואידך
                while self.position < len(self.tokens):
                    next_token = self.current_token()
                    if next_token.type == 'KEYWORD' and next_token.value == 'אי_נמי':
                        self.advance()
                        self.expect('DELIMITER', '(')
                        elif_condition = self.parse_expression()
                        self.expect('DELIMITER', ')')
                        self.expect('DELIMITER', '{')
                        elif_branch = self.parse_block()
                        branches.append(('ELIF', elif_condition, elif_branch))
    
                    elif next_token.type == 'KEYWORD' and next_token.value == 'אידך':
                        self.advance()
                        self.expect('DELIMITER', '{')
                        else_branch = self.parse_block()
                        branches.append(('ELSE', else_branch))
                        break
                    
                    else:
                        break
                    
                return ('IF_CHAIN', branches)

            elif token.value == 'הדרן_עלך':  # לולאת while
                self.advance()
                self.expect('DELIMITER', '(')
                condition = self.parse_expression()  # תנאי הלולאה
                self.expect('DELIMITER', ')')
                self.expect('DELIMITER', '{')
                body = self.parse_block()  # גוף הלולאה
                return ('WHILE_LOOP', condition, body)

        elif token.type == 'IDENTIFIER':
            var_name = token.value
            self.advance()
            # בדיקת גישה למערך (var[index])
            if self.current_token().type == 'DELIMITER' and self.current_token().value == '[':
                self.advance()  # דילוג על '['
                index_expr = self.parse_expression()
                self.expect('DELIMITER', ']')

                # בדיקת אופרטור השמה
                operator_token = self.current_token()
                if operator_token.type == 'OPERATOR' and operator_token.value == '=':
                    self.advance()
                    value_expr = self.parse_expression()
                    return ('ARRAY_ASSIGN', var_name, index_expr, value_expr)
                else:
                    raise SyntaxError("ציפיתי לאופרטור השמה '=' לאחר גישה למערך")
            else:
                # טיפול בהשמה למשתנה
                operator_token = self.current_token()

                if operator_token.type == 'OPERATOR' and operator_token.value in ('﬩﬩', '++', '--'):
                    op = operator_token.value
                    self.advance()
                    if op in ('﬩﬩', '++'):
                        return ('INCREMENT', var_name, 'POSTFIX')
                    else:
                        return ('DECREMENT', var_name, 'POSTFIX')

                elif operator_token.type == 'OPERATOR' and operator_token.value in ('﬩=', '+=', '-=', '*=', '/=', '%='):
                    op = operator_token.value[0]
                    self.advance()
                    if op == '﬩':
                        op = '+'
                    expr = self.parse_expression()
                    return ('VAR_REASSIGN', var_name, ('BINARY_OP', op, ('VAR', var_name), expr))

                elif operator_token.type == 'OPERATOR' and operator_token.value == '=':
                    self.advance()
                    expr = self.parse_expression()
                    return ('VAR_REASSIGN', var_name, expr)

                else:
                    return ('VAR', var_name)

        elif token.type == 'OPERATOR' and token.value in ('﬩﬩', '++', '--'):
            op = token.value
            self.advance()
            var_name = self.expect('IDENTIFIER')
            if op in ('﬩﬩', '++'):
                return ('INCREMENT', var_name, 'PREFIX')
            else:
                return ('DECREMENT', var_name, 'PREFIX')

        else:
            raise SyntaxError(f"לא ניתן לנתח את הפקודה: {token.value}")

    def parse_block(self):
        statements = []
        while self.position < len(self.tokens) and self.current_token().value != '}':
            statements.append(self.parse_statement())
        self.expect('DELIMITER', '}')
        return statements

    def parse_expression(self):
        # יצירת ביטוי עבור הפעולות החשבוניות
        left = self.parse_term()
        
        # לולאת פעולות חיבור וחיסור
        while self.position < len(self.tokens):
            token = self.current_token()
            
            if token.type == 'OPERATOR' and token.value in ('﬩', '+', '-'):
                self.advance()
                if token.value == '﬩':
                    token.value = '+'
                right = self.parse_term()
                left = ('BINARY_OP', token.value, left, right)
            else:
                break
            
        # בדיקה עבור פעולת השוואה
        if self.position < len(self.tokens):
            token = self.current_token()
            if token.type == 'OPERATOR' and token.value in ('==', '!=', '>', '<', '>=', '<='):
                self.advance()
                right = self.parse_expression()  # קריאה חוזרת ל-parse_expression כדי לאפשר ביטויים מורכבים
                return ('COMPARE_OP', token.value, left, right)
        
        return left

    def parse_term(self):
        left = self.parse_factor()
        
        while self.position < len(self.tokens):
            token = self.current_token()
            
            if token.type == 'OPERATOR' and token.value in ('*', '/'):
                self.advance()
                right = self.parse_factor()
                left = ('BINARY_OP', token.value, left, right)
            else:
                break
        
        return left

    def parse_factor(self):
        token = self.current_token()

        if token.type == 'NUMBER':
            self.advance()
            return ('NUMBER', int(token.value))

        elif token.type == 'STRING':
            self.advance()
            return ('STRING', token.value)

        elif token.type == 'IDENTIFIER':
            var_name = token.value
            self.advance()
            # בדיקת גישה למערך (var[index])
            if self.position < len(self.tokens) and self.current_token().type == 'DELIMITER' and self.current_token().value == '[':
                self.advance()  # דילוג על '['
                index_expr = self.parse_expression()
                self.expect('DELIMITER', ']')
                return ('ARRAY_ACCESS', var_name, index_expr)
            else:
                return ('VAR', var_name)

        elif token.type == 'DELIMITER' and token.value == '[':
            # יצירת מערך חדש
            self.advance()
            elements = []
            while self.position < len(self.tokens) and self.current_token().value != ']':
                element = self.parse_expression()
                elements.append(element)
                if self.current_token().value == ',':
                    self.advance()
                else:
                    break
            self.expect('DELIMITER', ']')
            return ('ARRAY', elements)

        elif token.type == 'KEYWORD' and token.value == 'בעא_מיניה':
            self.advance()
            self.expect('DELIMITER', '(')
            try:
                prompt = self.parse_expression()
            except:
                prompt = ""
            self.expect('DELIMITER', ')')
            return ('INPUT', prompt)

        elif token.type == 'KEYWORD' and token.value == 'אין':
            self.advance()
            return ('BOOLEAN', True)

        elif token.type == 'KEYWORD' and token.value == 'לא':
            self.advance()
            return ('BOOLEAN', False)

        elif token.type == 'DELIMITER' and token.value == '(':
            self.advance()
            expr = self.parse_expression()
            self.expect('DELIMITER', ')')
            return expr

        raise SyntaxError(f"לא ניתן לנתח את הביטוי: {token.value}")

    def current_token(self):
        return self.tokens[self.position]

    def advance(self):
        self.position += 1

    def expect(self, token_type, value=None):
        token = self.current_token()
        if token.type != token_type or (value and token.value != value):
            raise SyntaxError(f"ציפיתי ל-{token_type} {value} אבל קיבלתי {token.type} {token.value}")
        self.advance()
        return token.value