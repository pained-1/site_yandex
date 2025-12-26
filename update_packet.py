#!/usr/bin/env python
import json
import subprocess
import sys

import pkg_resources

# Получаем список установленных пакетов
installed_packages = [(d.project_name, d.version) for d in pkg_resources.working_set]

# Создаем резервную копию версий
with open('package_backup.txt', 'w') as f:
    for package, version in installed_packages:
        f.write(f"{package}=={version}\n")

print("Создана резервная копия пакетов в package_backup.txt")

# Получаем список устаревших пакетов
outdated = subprocess.check_output([sys.executable, '-m', 'pip', 'list', '--outdated', '--format=json']).decode('utf-8')
outdated_packages = json.loads(outdated)

# Обновляем каждый пакет по отдельности
for package in outdated_packages:
    package_name = package['name']
print(f"Обновление {package_name}...")
try:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', package_name])
    print(f"Успешно обновлен {package_name}")
except Exception as e:
    print(f"Ошибка при обновлении {package_name}: {e}")

print("Процесс обновления завершен!")
