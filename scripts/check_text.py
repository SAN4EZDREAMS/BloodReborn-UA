import os
import xml.etree.ElementTree as ET
import hunspell
import pandas as pd
from language_tool_python import LanguageTool

# 🔹 Ініціалізація мовних інструментів
hspell = hunspell.HunSpell('/usr/share/hunspell/uk_UA.dic', '/usr/share/hunspell/uk_UA.aff')
lt = LanguageTool('uk-UA')

# 🔹 Функція перевірки орфографії
def check_spelling(word):
    return hspell.spell(word)

# 🔹 Функція перевірки граматики
def check_grammar(text):
    return lt.check(text)

# 🔹 Список папок для перевірки
target_dirs = ["Item", "Menu"]

# 🔹 Список для збереження помилок
errors = []

# 🔹 Обхід тільки папок `Item` та `Menu`
for target_dir in target_dirs:
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(root, file)

                # 🔹 Парсимо XML
                tree = ET.parse(file_path)
                root_elem = tree.getroot()

                for text_elem in root_elem.findall(".//text"):
                    text_id = text_elem.get("id", "Unknown")
                    text_content = text_elem.text.strip() if text_elem.text else ""

                    # 🔹 Ігноруємо пусті рядки, `%null%` або лише `*`
                    if text_content in ("%null%", "*") or text_content.strip() == "":
                        continue

                    # 🔹 Орфографічна перевірка
                    words = text_content.split()
                    for word in words:
                        if not check_spelling(word):
                            errors.append(["SPELLING", file_path, text_id, text_content, word, "Невірне написання"])

                    # 🔹 Граматична перевірка
                    matches = check_grammar(text_content)
                    for match in matches:
                        errors.append(["GRAMMAR", file_path, text_id, text_content, match.ruleId, match.message])

# 🔹 Якщо є помилки – зберігаємо в Excel
if errors:
    df = pd.DataFrame(errors, columns=["Тип помилки", "Файл", "ID", "Оригінальний текст", "Помилкове слово/Правило", "Опис"])
    df.to_excel("text_check_report.xlsx", index=False)
