#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#created by: Pushkarev Aleksandr

import nuke
import os, json, getpass

curDir = os.path.dirname(__file__).replace("\\","/")  # Текущая папка
users_settings_path = curDir+"/users_settings.json"  # Файл с настройками пользователей
plugins_info_path = curDir+"/plugins_info.json"  # Файл с информацией о плагинах

def current_user() -> str:
    return getpass.getuser().lower()

def getPluginsSettings(name: str) -> bool:
    """
    Функция возвращает включать или нет плагин по имени name для текущего пользователя.
    Если для пользователя нет настроек или нет настроек для конкретного плагина, то вернет значение по умолчанию.
    Если для плагина нет значения по умолчанию, то вернет True
    """
    # Проверим в настройках для пользователя
    if os.path.isfile(users_settings_path):
        with open(users_settings_path, "r", encoding="utf-8") as file:
            users_settings = json.load(file)
        user = current_user()
        if user in users_settings and name in users_settings[user]:
            return users_settings[user][name]
    
    # Если не получилось получить настройки у пользователя, возьмем настройки по умолчанию
    if os.path.isfile(plugins_info_path):
        with open(plugins_info_path, "r", encoding="utf-8") as file:
            plugins_info = json.load(file)
        for plugins in plugins_info.values():
            if name in plugins:
                return plugins[name].get("default", True)
    return True

def loadPlugins(target_dir: str, not_gui_load: bool) -> None:
    """
    Загружает плагины в указанной папке на основе пользовательских настроек и информации о плагинах(работает через getPluginsSettings)
    Args:
        target_dir (str): Путь к директории, содержащей подпапки с плагинами.
        not_gui_load (bool): True означает что если мы сейчас не в GUI режиме(рендер на ферме), то плагин загрузим даже если он выключен у пользователя.
            Ставим False для плагинов из GizmoPacks потому что они загружаются в виде группы и не нужно во время рендера добавлять папки в pluginPath
    """
    for d in reversed(os.listdir(target_dir)):  # Проходимся по папкам в текущей директории(в обратном порядке чтобы было по алфавиту)
        if os.path.isdir(os.path.join(target_dir, d)) and (getPluginsSettings(d) or (not nuke.GUI and not_gui_load)):
            nuke.pluginAddPath(os.path.join(target_dir, d))
