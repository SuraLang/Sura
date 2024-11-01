import argparse
from lexer import lexer
from parser import Parser
from interpreter import Interpreter

def main():
    # הגדרת ארגומנט לשורת הפקודה
    parser = argparse.ArgumentParser(description='הרץ קובץ סורא.')
    parser.add_argument('filename', type=str, help='שם הקובץ של קוד סורא (כולל סיומת .סורא)')
    
    # קבלת הארגומנט
    args = parser.parse_args()
    filename = args.filename

    # קריאת התוכן של הקובץ
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            code = file.read()
    except FileNotFoundError:
        print(f"שגיאה: הקובץ '{filename}' לא נמצא.")
        return
    except Exception as e:
        print(f"שגיאה במהלך קריאת הקובץ: {e}")
        return

    # עיבוד הקוד
    tokens = lexer(code)
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter(ast)
    interpreter.execute()

if __name__ == '__main__':
    main()