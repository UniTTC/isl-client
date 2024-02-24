# Пример кода в update_version.py
import semver  # Предполагается, что вы используете semver для управления версиями

# Получение текущей версии
with open("VERSION", "r") as version_file:
    current_version = version_file.read().strip()

# Инкремент версии
new_version = semver.bump_patch(current_version)

# Обновление файла VERSION
with open("VERSION", "w") as version_file:
    version_file.write(new_version)

# Печать новой версии для передачи в следующий шаг GitHub Actions
print(f"::set-output name=new_version::{new_version}")
