# --- ส่วนที่ 1: AST Nodes ---
class AssignmentNode:
    def __init__(self, name, value_node):
        self.name = name; self.value_node = value_node
class PrintNode:
    def __init__(self, value_node): self.value_node = value_node
class BinOpNode:
    def __init__(self, left, op, right):
        self.left = left; self.op = op; self.right = right
class NumberNode:
    def __init__(self, value): self.value = value
class VarNode:
    def __init__(self, name): self.name = name
class StringNode:
    def __init__(self, value): self.value = value
# โหนดสำหรับการวนลูป
class WhileNode:
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body
#  โหนดสำหรับการรับค่าจากคีย์บอร์ด
class InputNode:
    def __init__(self, prompt_node):
        self.prompt_node = prompt_node
#  โหนดสำหรับการเปรียบเทียบ (เช่น > , < , ==)
class CompareNode:
    def __init__(self, left, op, right):
        self.left = left; self.op = op; self.right = right

class FunctionDefNode:
    def __init__(self, name, params, body):
        self.name = name; self.params = params; self.body = body

class FunctionCallNode:
    def __init__(self, name, args):
        self.name = name; self.args = args

# โหนดสำหรับ ถ้า...มิฉะนั้น
class IfNode:
    def __init__(self, condition, true_block, false_block):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block

# --- ส่วนที่ 2: The Parser ---
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    
    def peek_token(self):
        """แอบดู Token ตัวถัดไปโดยที่ยังไม่ขยับตำแหน่ง"""
        next_pos = self.pos + 1
        if next_pos < len(self.tokens):
            return self.tokens[next_pos]
        return None

    def eat(self, token_type):
        token = self.current_token()
        if token and token['ประเภท'] == token_type:
            self.pos += 1
            return token
        raise Exception(f"Syntax Error! คาดหวัง '{token_type}' แต่เจอ {token}")

    def parse(self):
        return self.parse_block()

    #  ฟังก์ชันอ่านโค้ดเป็นบล็อก (ใช้อ่านโค้ดในปีกกา หรืออ่านทั้งไฟล์)
    def parse_block(self):
        statements = []
        while self.current_token() and self.current_token()['ประเภท'] != 'RBRACE':
            token = self.current_token()
            
            if token['ค่า'] == 'สร้างฟังก์ชัน':
                statements.append(self.parse_function_def())
            if token['ประเภท'] == 'KEYWORD' and token['ค่า'] == 'ให้':
                statements.append(self.parse_assignment())
            elif token['ประเภท'] == 'KEYWORD' and token['ค่า'] == 'แสดง':
                statements.append(self.parse_print())
            elif token['ประเภท'] == 'KEYWORD' and token['ค่า'] == 'ถ้า':
                statements.append(self.parse_if())
            
            elif token['ประเภท'] == 'KEYWORD' and token['ค่า'] == 'ตราบที่':
                statements.append(self.parse_while())
            elif token['ประเภท'] == 'ID' and self.peek_token() and self.peek_token()['ประเภท'] == 'LPAREN':
                statements.append(self.parse_function_call())
            else:
                self.pos += 1 
        return statements
    
    def parse_function_def(self):
        self.eat('KEYWORD') # สร้างฟังก์ชัน
        name = self.eat('ID')['ค่า']
        self.eat('LPAREN')
        params = []
        if self.current_token()['ประเภท'] == 'ID':
            params.append(self.eat('ID')['ค่า'])
        self.eat('RPAREN')
        self.eat('LBRACE')
        body = self.parse_block()
        self.eat('RBRACE')
        return FunctionDefNode(name, params, body)
    
    def parse_function_call(self):
        name = self.eat('ID')['ค่า']
        self.eat('LPAREN')
        args = [] 
        if self.current_token()['ประเภท'] != 'RPAREN':
            args.append(self.parse_expression())
        self.eat('RPAREN')
        return FunctionCallNode(name, args)

    #  ฟังก์ชันอ่านลูป ตราบที่
    def parse_while(self):
        self.eat('KEYWORD') 
        
        # อ่านเงื่อนไข (เช่น รอบ < 4)
        left = self.parse_expression()
        op = self.current_token()
        if op['ประเภท'] in ('GT', 'LT', 'EQ', 'NEQ'):
            self.eat(op['ประเภท'])
        right = self.parse_expression()
        condition = CompareNode(left, op, right)

        # อ่านบล็อกคำสั่งที่ต้องวนซ้ำ { ... }
        self.eat('LBRACE')
        body = self.parse_block()
        self.eat('RBRACE')

        return WhileNode(condition, body)

    def parse_assignment(self):
        self.eat('KEYWORD')
        name_token = self.eat('ID')
        self.eat('ASSIGN')
        expr_node = self.parse_expression()
        return AssignmentNode(name_token['ค่า'], expr_node)

    def parse_print(self):
        self.eat('KEYWORD')
        self.eat('LPAREN')
        expr_node = self.parse_expression()
        self.eat('RPAREN')
        return PrintNode(expr_node)

    #  ฟังก์ชันอ่านเงื่อนไข ถ้า...มิฉะนั้น
    def parse_if(self):
        self.eat('KEYWORD') # ข้ามคำว่า "ถ้า"
        
        # อ่านเงื่อนไข (เช่น คะแนน > 50)
        left = self.parse_expression()
        op = self.current_token()
        if op['ประเภท'] in ('GT', 'LT', 'EQ', 'NEQ'):
            self.eat(op['ประเภท'])
        right = self.parse_expression()
        condition = CompareNode(left, op, right)

        # อ่านบล็อกเมื่อเป็นจริง { ... }
        self.eat('LBRACE')
        true_block = self.parse_block()
        self.eat('RBRACE')

        # อ่านบล็อกเมื่อเป็นเท็จ (มิฉะนั้น)
        false_block = None
        if self.current_token() and self.current_token()['ค่า'] == 'มิฉะนั้น':
            self.eat('KEYWORD')
            self.eat('LBRACE')
            false_block = self.parse_block()
            self.eat('RBRACE')

        return IfNode(condition, true_block, false_block)

    # ส่วนคณิตศาสตร์
    def parse_factor(self):
        token = self.current_token()
        if token['ประเภท'] == 'NUMBER':
            self.eat('NUMBER')
            return NumberNode(int(token['ค่า']))
        elif token['ประเภท'] == 'ID':
            self.eat('ID')
            return VarNode(token['ค่า'])
        elif token['ประเภท'] == 'STRING':
            self.eat('STRING')
            return StringNode(token['ค่า'].strip("\"'"))
        
        elif token['ประเภท'] == 'KEYWORD' and token['ค่า'] == 'รับค่า':
            self.eat('KEYWORD') # ข้ามคำว่า "รับค่า"
            self.eat('LPAREN')  # ข้ามวงเล็บเปิด "("
            prompt_node = self.parse_expression() # อ่านข้อความคำถามข้างในวงเล็บ
            self.eat('RPAREN')  # ข้ามวงเล็บปิด ")"
            return InputNode(prompt_node)

    def parse_term(self):
        node = self.parse_factor()
        while self.current_token() and self.current_token()['ประเภท'] in ('MUL', 'DIV'):
            token = self.current_token()
            self.eat(token['ประเภท'])
            node = BinOpNode(left=node, op=token, right=self.parse_factor())
        return node

    def parse_expression(self):
        node = self.parse_term()
        while self.current_token() and self.current_token()['ประเภท'] in ('PLUS', 'MINUS'):
            token = self.current_token()
            self.eat(token['ประเภท'])
            node = BinOpNode(left=node, op=token, right=self.parse_term())
        return node
    
    
    