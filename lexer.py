import re

TOKEN_RULES = [
    ('ID',        r'[a-zA-Z_ก-๙][a-zA-Z0-9_ก-๙]*'), 
    ('NUMBER',    r'\d+'),
    
    ('EQ',        r'=='),                   # เท่ากับ (ต้องอยู่ก่อน ASSIGN)
    ('NEQ',       r'!='),                   # ไม่เท่ากับ
    ('ASSIGN',    r'='),                    # ประกาศตัวแปร
    ('GT',        r'>'),                    # มากกว่า
    ('LT',        r'<'),                    # น้อยกว่า
    
    ('PLUS',      r'\+'),                   
    ('MINUS',     r'-'),                    
    ('MUL',       r'\*'),                   
    ('DIV',       r'/'),                    
    ('LPAREN',    r'\('),                   
    ('RPAREN',    r'\)'),                   
    ('LBRACE',    r'\{'),                   
    ('RBRACE',    r'\}'),                   
    ('STRING',    r'".*?"|\'.*?\''),        
    ('SKIP',      r'[ \t]+'),               
    ('NEWLINE',   r'\n'),                   
    ('MISMATCH',  r'.'),                    
]

def lexer(code):
    tokens = []
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in TOKEN_RULES)
    line_num = 1
    
    for mo in re.finditer(tok_regex, code):
        kind = mo.lastgroup
        value = mo.group()
        
        if kind == 'NEWLINE':
            line_num += 1
            continue
        elif kind == 'SKIP':
            continue
        elif kind == 'MISMATCH':
            raise RuntimeError(f'ไม่รู้จักคำสั่ง: {value!r} ในบรรทัดที่ {line_num}')
            
        #  เช็คว่าเป็น Keyword ภาษาไทยไหม ถ้าใช่ให้เปลี่ยนประเภท
        if kind == 'ID' and value in ['ให้', 'แสดง', 'ถ้า', 'มิฉะนั้น', 'และ', 'หรือ','ตราบที่','รับค่า', 'สร้างฟังก์ชัน', 'ส่งคืน']:
            kind = 'KEYWORD'
            
        tokens.append({'ประเภท': kind, 'ค่า': value, 'บรรทัด': line_num})
        
    return tokens
