from errors import ThaiScriptError

class Interpreter:
    def __init__(self):
        
        self.scopes = [{}] 
        self.functions = {} 
    
    def get_current_scope(self):
        return self.scopes[-1]

    def visit(self, node):
        method_name = f'visit_{type(node).__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node):
        # เปลี่ยนไปใช้ Error ของเราเอง
        raise ThaiScriptError(f"ระบบยังไม่รู้จักคำสั่ง: {type(node).__name__}", "??")

    # --- การประมวลผลข้อมูล ---
    def visit_NumberNode(self, node):
        return node.value

    def visit_StringNode(self, node):
        return node.value

    def visit_VarNode(self, node):
        # ค้นหาตัวแปรจาก Scope ล่าสุด (Local) ย้อนกลับไปหา Global
        for scope in reversed(self.scopes):
            if node.name in scope:
                return scope[node.name]
        
        # ถ้าหาไม่เจอจริงๆ ค่อยแจ้ง Error
        raise ThaiScriptError(f"ไม่พบตัวแปรชื่อ '{node.name}' ในความจำ", "??")

    def visit_BinOpNode(self, node):
        left_val = self.visit(node.left)
        right_val = self.visit(node.right)

        if node.op['ประเภท'] == 'PLUS': return left_val + right_val
        if node.op['ประเภท'] == 'MINUS': return left_val - right_val
        if node.op['ประเภท'] == 'MUL': return left_val * right_val
        if node.op['ประเภท'] == 'DIV': return left_val / right_val

    # --- การประกาศตัวแปรและการแสดงผล ---
    def visit_AssignmentNode(self, node):
        # เก็บค่าลงใน Scope ปัจจุบันแทน env
        val = self.visit(node.value_node)
        self.get_current_scope()[node.name] = val

    def visit_PrintNode(self, node):
        result = self.visit(node.value_node)
        print(result)

    
    # ระบบฟังก์ชัน (Functions)
    
    def visit_FunctionDefNode(self, node):
        
        self.functions[node.name] = node

    def visit_FunctionCallNode(self, node):
        if node.name not in self.functions:
            raise ThaiScriptError(f"ไม่พบฟังก์ชันชื่อ '{node.name}'", "??")
            
        func_node = self.functions[node.name]
        
        # (Local Scope)
        new_scope = {}
        
        # ใส่ค่าที่ส่งมา (Args) ลงในตัวแปรรับค่า (Params)
        if len(node.args) > 0 and len(func_node.params) > 0:
            val = self.visit(node.args[0])
            param_name = func_node.params[0]
            new_scope[param_name] = val
            
        #  สวมกล่องความจำเข้าไปใน Stack
        self.scopes.append(new_scope)
        
        # รันโค้ดข้างในฟังก์ชัน
        for stmt in func_node.body:
            self.visit(stmt)
            
        #โยนกล่องความจำทิ้งไปเมื่อทำงานเสร็จ (Clear Local Memory)
        self.scopes.pop()

    
    # --- Control Flow (เงื่อนไขและลูป) ---
   
    def visit_CompareNode(self, node):
        left_val = self.visit(node.left)
        right_val = self.visit(node.right)

        if node.op['ประเภท'] == 'GT': return left_val > right_val
        if node.op['ประเภท'] == 'LT': return left_val < right_val
        if node.op['ประเภท'] == 'EQ': return left_val == right_val
        if node.op['ประเภท'] == 'NEQ': return left_val != right_val

    def visit_IfNode(self, node):
        condition_result = self.visit(node.condition)
        if condition_result:
            for stmt in node.true_block:
                self.visit(stmt)
        elif node.false_block is not None:
            for stmt in node.false_block:
                self.visit(stmt)

    def visit_WhileNode(self, node):
        while self.visit(node.condition): 
            for stmt in node.body:        
                self.visit(stmt)

    def visit_InputNode(self, node):
        prompt_text = self.visit(node.prompt_node)
        user_input = input(str(prompt_text))
        try:
            return int(user_input)
        except ValueError:
            return user_input

    def execute(self, ast_tree):
        for node in ast_tree:
            self.visit(node)