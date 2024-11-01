class Interpreter:
    def __init__(self, ast):
        self.ast = ast
        self.variables = {}

    def execute(self):
        for statement in self.ast:
            self.execute_statement(statement)

    def execute_statement(self, statement):
        stype = statement[0]

        if stype == 'PRINT':
            expr = statement[1]
            value = self.evaluate_expression(expr)
            print(value)

        elif stype == 'VAR_ASSIGN':
            var_name = statement[1]
            expr = statement[2]
            value = self.evaluate_expression(expr)
            self.variables[var_name] = value
        
        elif stype == 'VAR_REASSIGN':
            # שינוי ערך משתנה קיים
            var_name = statement[1]
            expr = statement[2]
            if var_name in self.variables:
                value = self.evaluate_expression(expr)
                self.variables[var_name] = value
            else:
                raise NameError(f"המשתנה '{var_name}' לא הוגדר קודם לכן")

        elif stype == 'IF':
            condition = self.evaluate_expression(statement[1])
            true_branch = statement[2]
            false_branch = statement[3]

            if condition:
                for stmt in true_branch:
                    self.execute_statement(stmt)
            elif false_branch:
                if false_branch[0] == 'IF':  # elif condition
                    elif_condition = self.evaluate_expression(false_branch[1])
                    elif_branch = false_branch[2]
                    if elif_condition:
                        for stmt in elif_branch:
                            self.execute_statement(stmt)
                else:  # else branch
                    for stmt in false_branch:
                        self.execute_statement(stmt)

        elif stype == 'IF_CHAIN':
            for branch in statement[1]:
                if branch[0] == 'IF' or branch[0] == 'ELIF':
                    condition = self.evaluate_expression(branch[1])
                    if condition:
                        for stmt in branch[2]:
                            self.execute_statement(stmt)
                        break
                elif branch[0] == 'ELSE':
                    for stmt in branch[1]:
                        self.execute_statement(stmt)
                    break

        elif stype == 'WHILE_LOOP':  # ביצוע לולאה
            condition = statement[1]
            body = statement[2]
            while self.evaluate_expression(condition):
                for stmt in body:
                    self.execute_statement(stmt)

        elif stype == 'ARRAY_ASSIGN':
            var_name = statement[1]
            index_expr = statement[2]
            value_expr = statement[3]
            index = self.evaluate_expression(index_expr)
            value = self.evaluate_expression(value_expr)

            if var_name in self.variables:
                array = self.variables[var_name]
                if isinstance(array, list):
                    try:
                        array[index] = value
                    except IndexError:
                        raise IndexError(f"אינדקס {index} מחוץ לטווח המערך")
                else:
                    raise TypeError(f"{var_name} אינו מערך")

        elif stype == 'INCREMENT':
            var_name = statement[1]
            mode = statement[2]  # 'PREFIX' או 'POSTFIX'
            if var_name in self.variables:
                if isinstance(self.variables[var_name], int):
                    if mode == 'PREFIX':
                        self.variables[var_name] += 1
                    elif mode == 'POSTFIX':
                        self.variables[var_name] += 1
                else:
                    raise TypeError(f"המשתנה {var_name} אינו מספר")
            else:
                raise NameError(f"המשתנה {var_name} לא הוגדר")

        elif stype == 'DECREMENT':
            var_name = statement[1]
            mode = statement[2]
            if var_name in self.variables:
                if isinstance(self.variables[var_name], int):
                    if mode == 'PREFIX':
                        self.variables[var_name] -= 1
                    elif mode == 'POSTFIX':
                        self.variables[var_name] -= 1
                else:
                    raise TypeError(f"המשתנה {var_name} אינו מספר")
            else:
                raise NameError(f"המשתנה {var_name} לא הוגדר")

    def evaluate_expression(self, expr):
        etype = expr[0]

        if etype == 'NUMBER':
            return expr[1]

        elif etype == 'STRING':
            return expr[1]

        elif etype == 'VAR':
            var_name = expr[1]
            if var_name in self.variables:
                return self.variables[var_name]
            raise NameError(f"המשתנה {var_name} לא הוגדר")

        elif etype == 'INPUT':
            prompt = self.evaluate_expression(expr[1]) if expr[1] else ""
            return input(prompt)

        elif etype == 'BINARY_OP':
            op = expr[1]
            left = self.evaluate_expression(expr[2])
            right = self.evaluate_expression(expr[3])

            if op == '+':
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            elif op == '-':
                return left - right
            elif op == '*':
                return left * right
            elif op == '/':
                return left / right

        elif etype == 'BOOLEAN':
            return expr[1]

        elif etype == 'COMPARE_OP':
            op = expr[1]
            left = self.evaluate_expression(expr[2])
            right = self.evaluate_expression(expr[3])

            if op == '==':
                return left == right
            elif op == '!=':
                return left != right
            elif op == '>':
                return left > right
            elif op == '<':
                return left < right
            elif op == '>=':
                return left >= right
            elif op == '<=':
                return left <= right
            
        elif etype == 'ARRAY':
            elements = [self.evaluate_expression(element) for element in expr[1]]
            return elements

        elif etype == 'ARRAY_ACCESS':
            var_name = expr[1]
            index = self.evaluate_expression(expr[2])
            if var_name in self.variables:
                array = self.variables[var_name]
                if isinstance(array, list):
                    try:
                        return array[index]
                    except IndexError:
                        raise IndexError(f"אינדקס {index} מחוץ לטווח המערך")
                else:
                    raise TypeError(f"{var_name} אינו מערך")
            else:
                raise NameError(f"המשתנה {var_name} לא הוגדר")

        raise SyntaxError("שגיאה בחישוב הביטוי")