import os
import ast

class LanguageDetector:
    def __init__(self, directories):
        self.directories = directories

    def detect_python_files(self):
        python_files = []
        for directory in self.directories:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py'):
                        python_files.append(os.path.join(root, file))
        return python_files

    def analyze_syntax(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
            try:
                ast.parse(content)
                return True, "Syntax is correct"
            except SyntaxError as e:
                return False, f"Syntax error in {file_path}: {e}"

# Example usage:
# detector = LanguageDetector(['path/to/directory'])
# python_files = detector.detect_python_files()
# for file in python_files:
#     valid, message = detector.analyze_syntax(file)
#     print(f'{file}: {message}')