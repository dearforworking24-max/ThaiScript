class ThaiScriptError(Exception):
    def __init__(self, message, line):
        self.message = message
        self.line = line
    def __str__(self):
        return f"❌ เกิดข้อผิดพลาดในบรรทัดที่ {self.line}: {self.message}"
