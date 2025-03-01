import os
import re
import pandas as pd
import hunspell
from language_tool_python import LanguageTool

# Ініціалізація перевірки орфографії та граматики
spell = hunspell.HunSpell("/usr/share/hunspell/uk_UA.dic", "/usr/share/hunspell/uk_UA.aff")
tool = LanguageTool("uk")

# Папки для перевірки
TARGET_DIRS = ["Lang_check"]
REPORT_FILE = "scripts/spellcheck_report.xlsx"

# Фільтрація тексту в XML
def extract_text_from_xml(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    matches = re.findall(r'<text id="\d+">([^<]*)</text>', content)
    return [text.strip() for text in matches if text.strip() and not re.match(r"^[\*\%]+$", text.strip())]

# Пошук усіх XML-файлів у папках
def find_xml_files():
    xml_files = []
    for target_dir in TARGET_DIRS:
        for root, _, files in os.walk(target_dir):
            for file in files:
                if file.endswith(".xml"):
                    xml_files.append(os.path.join(root, file))
    return xml_files

# Перевірка файлів
def check_files():
    results = []
    
    for file in find_xml_files():
        texts = extract_text_from_xml(file)
        
        for text in texts:
            # Орфографія (через hunspell)
            words = re.findall(r'\b\w+\b', text)
            spelling_errors = [word for word in words if not spell.spell(word)]

            # Граматика (LanguageTool)
            grammar_matches = [
                match for match in tool.check(text)
                if match.ruleId not in ["MORFOLOGIK_RULE_UK_UA"]
            ]

            # Додавання в звіт
            for word in spelling_errors:
                results.append([file, text, "Орфографічна помилка", word, "—"])

            for match in grammar_matches:
                results.append([file, text, "Граматична помилка", match.ruleId, match.replacements])

    return results

# Створення звіту
def create_report():
    errors = check_files()
    if not errors:
        print("✅ Помилок не знайдено!")
        return

    df = pd.DataFrame(errors, columns=["Файл", "Текст", "Тип помилки", "Помилка", "Пропоноване виправлення"])
    df.to_excel(REPORT_FILE, index=False)
    print(f"📄 Звіт збережено: {REPORT_FILE}")

if __name__ == "__main__":
    create_report()
