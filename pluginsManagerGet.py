#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#created by: Pushkarev Aleksandr

import nuke
import os, json, getpass

json_path = os.path.dirname(__file__).replace('\\','/')+'/pluginsManager.json'#файл с настройками пользователей

def getPluginsSettings(name: str) -> bool:
    """
    Функция возвращает включать или нет плагин по имени name для текущего пользователя.
    Если для пользователя нет настроек или нет настроек для конкретного плагина, то вернет True.
    TODO Если у пользователя нет настроек, нужно возвращать дефолтное значение для плагина, а не True
    """
    if os.path.isfile(json_path):
        with open(json_path,'r') as f:
            json_data = json.load(f)
        if getpass.getuser() in json_data:
            return json_data.get(getpass.getuser()).get(name, True)
    return True

def loadPlugins(target_dir: str, not_gui_load: bool) -> None:
    """
    Проходимся по папкам в текущей директории(нужно передать путь до папки в target_dir, это может быть любая папка которая содержит папки с плагинами).
    Включаем плагин если нет файла настроек или у пользователя нет настроек или у пользователя нет настроек для этого плагина, если настройка есть включаем или нет в зависимости от настройки.
    Включение означает просто добавить эту папку в plugin path.
    not_gui_load True означает что если мы сейчас не в GUI режиме(рендер на ферме), то плагин загрузим даже если он выключен у пользователя.
    Ставим False для плагинов из GizmoPacks потому что они загружаются в виде группы и не нужно во время рендера добавлять папки в pluginPath
    TODO Если у пользователя нет настроек, нужно ориентироваться на дефолтные настройки плагинов, а не включать принудительно
    """
    json_data = None
    if os.path.isfile(json_path):  # Если такой файл есть, читаем инфу из него
        with open(json_path,'r') as f:
            json_data = json.load(f)
    user_settings = json_data.get(getpass.getuser(), {}) if json_data else {}  # Создаем пустой словарь если нет файла или для пользователя нет настроек, чтобы потом по дефолту получить True
    for d in reversed(os.listdir(target_dir)):  # Проходимся по папкам в текущей директории(в обратном порядке чтобы было по алфавиту)
        if os.path.isdir(os.path.join(target_dir, d)) and (user_settings.get(d, True) or (not nuke.GUI and not_gui_load)):
            nuke.pluginAddPath(os.path.join(target_dir, d))