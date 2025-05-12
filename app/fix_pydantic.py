import os

def fix_pydantic_imports():
    """Исправляет импорты Pydantic в файле config.py"""
    config_path = "app/config.py"
    
    # Проверяем существование файла
    if not os.path.exists(config_path):
        print(f"Файл {config_path} не найден!")
        return False
    
    # Читаем содержимое файла
    with open(config_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Проверяем, нужно ли исправление
    if "from pydantic import BaseSettings" in content:
        # Устанавливаем pydantic-settings
        os.system("pip install pydantic-settings")
        
        # Заменяем импорт
        content = content.replace(
            "from pydantic import BaseSettings",
            "from pydantic_settings import BaseSettings"
        )
        
        # Записываем обновленное содержимое
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print(f"Файл {config_path} успешно обновлен!")
        return True
    else:
        print(f"Импорт BaseSettings не найден в {config_path} или уже исправлен.")
        return False

if __name__ == "__main__":
    fix_pydantic_imports()