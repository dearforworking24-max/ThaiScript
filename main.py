from lexer import lexer
from parser import Parser
from interpreter import Interpreter # ดึง Interpreter เข้ามาใช้
from errors import ThaiScriptError
import sys

def run():
    if len(sys.argv) < 2:
        print("กรุณาระบุไฟล์ที่ต้องการรัน เช่น python main.py test.th")
        return
        
    filename = sys.argv[1]
    
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            code = file.read()
    except FileNotFoundError:
        print(f"ไม่พบไฟล์: {filename}")
        return
    try:
        tokens = lexer(code)
        parser = Parser(tokens)
        ast_tree = parser.parse()
        interpreter = Interpreter()
        interpreter.execute(ast_tree)
    except ThaiScriptError as e:
        print(e)
    except Exception as e:
        print(f"❌ เกิดข้อผิดพลาดร้ายแรง: {e}")

    # 1. ให้ Lexer หั่นคำ
    tokens = lexer(code)
    
    # 2. ให้ Parser สร้างแผนผัง AST
    parser = Parser(tokens)
    ast_tree = parser.parse()
    
    # 3. ให้ Interpreter ลงมือรัน
    print(f"--- ผลลัพธ์การรันโปรแกรม {filename} ---")
    interpreter = Interpreter()
    interpreter.execute(ast_tree)

if __name__ == "__main__":
    run()