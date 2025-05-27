#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#created by: Pushkarev Aleksandr

import nuke, nukescripts
import os, json, getpass, re, importlib, sys
from pathlib import Path

gp_name = 'GizmoPacks'  # Имя папки и менюшки для гизмо паков(должна совпадать с именем папки Z:/Nuke_Workgroup/gizmos/GizmoPacks)

curDir = os.path.dirname(__file__).replace("\\","/")  # Текущая папка
users_settings_path = curDir+'/users_settings.json'  # Файл с настройками пользователей
plugins_info_path = curDir+'/plugins_info.json'  # Файл с информацией о плагинах
nuke_workgroup_folder = str(Path(curDir).parent.parent).replace("\\","/")  # Путь до папки Z:/Nuke_Workgroup

def isPluginAvailable(plugin_name):
    """
    Проверяет доступен ли плагин в текущей версии нюка
    """
    dll_plugins = f"{nuke_workgroup_folder}/plugins/dll_plugins"  # Папка с dll плагинами, которые зависят от версии нюка
    plugin_folder = f"{dll_plugins}/{plugin_name}"  # Папка конкретного плагина
    if not os.path.isdir(plugin_folder):  # Если папки нет, значит плагин точно недоступен
        return False
    nuke_ver_lst = [f for f in os.listdir(plugin_folder) if re.fullmatch(r"Nuke\d+\.\d+",f) and os.path.isdir(f"{plugin_folder}/{f}")]  # Получаем список папок Nuke##.#
    if not nuke_ver_lst:  # Если версий нет, значит безверсионный плагин, значит доступен
        return True
    elif f"Nuke{nuke.NUKE_VERSION_MAJOR}.{nuke.NUKE_VERSION_MINOR}" in nuke_ver_lst:  # Иначе проверяем есть ли плагин для текущей версии
        return True
    else:
        return False 

class SettingsPanel(nukescripts.PythonPanel):
    def __init__(self, users_settings, plugins_info):
        super().__init__("Plugins Manager")
        self.setMinimumSize(350, 810)

        user_settings = users_settings.get(getpass.getuser())  # Получаем настройки плагинов для пользователя
        self.knDict = {}  # Коллектим все добавленные кнобы в виде словаря
        for pl_type, plugins in plugins_info.items():  # Проходимся по типам Plugins, OFX, Gizmo Packs, Gizmos
            self.addKnob(nuke.Text_Knob(pl_type.replace(' ','_'), pl_type+':'))  # Подпись для типов
            for i, (pl_name, pl_info) in enumerate(plugins.items()):  # Проходимся по плагинам для конкретного типа
                available = [" (недоступен)",""][isPluginAvailable(pl_name) or pl_type!="Plugins"]  # Проверяем доступен ли плагин, если плагин не доступен в текущей версии, делаем пометку
                kn = nuke.Boolean_Knob(pl_name, pl_info["label"]+available, pl_info["default"])  # Создаем чекбокс с дефолтным значением
                if user_settings and user_settings.get(pl_name)!=None:  # Если для пользователя есть настройки, то заменим на пользовательские настройки
                    kn.setValue(user_settings.get(pl_name))
                kn.setEnabled(pl_info["enabled"])  # Делаем кноб недоступным для редактирования для 3DE4 и NeatVideo
                if i!=0:  # Если кноб не первый, то начнем с новой строки, чтобы кнобы чекбоксы были друг под другом
                    kn.setFlag(nuke.STARTLINE)
                self.knDict[pl_name] = kn  # Добавляем кноб в словарь чтобы можно было позже получить к нему доступ
                self.addKnob(kn)

def pluginsManager():
    # Проверяем что есть файл с информацией о плагинах
    if not os.path.isfile(plugins_info_path):
        nuke.message("Нету файла с информацией о плагинах")
        return
    
    # Читаем информацию о плагинах
    with open(plugins_info_path, "r", encoding="utf-8") as file:
        plugins_info = json.load(file)

    # Если файла с настроками пользователей нету, создадим его и запишем в него пустой словарь
    if not os.path.isfile(users_settings_path):
        with open(users_settings_path, "w") as file:
            file.write("{}")
    
    # Читаем настройки из users_settings.json
    with open(users_settings_path, "r") as file:
        users_settings = json.load(file)
    
    panel = SettingsPanel(users_settings, plugins_info)
    if not panel.showModalDialog():
        return

    users_settings[getpass.getuser()] = {}  # Записываем в словарь настройки отмеченные пользователем
    for plugins in plugins_info.values():
        for pl_name in plugins:
            users_settings[getpass.getuser()][pl_name] = panel.knDict.get(pl_name).value()
    
    with open(users_settings_path, "w") as file:  # Записываем эти изменения в файл
        json.dump(users_settings, file, indent=4)

    gizmos_folder = f"{nuke_workgroup_folder}/gizmos"  # Папка с гизмами Z:/Nuke_Workgroup/gizmos
    for name in plugins_info["Gizmo Packs"]:  # Проходимся по всем пакам
        pack_menu = nuke.menu('Nodes').menu(f'{gp_name}/{name}')  # Ищем менюшку
        if panel.knDict.get(name).value():  # Если пользователь включил плагин(или он был включен)
            if not pack_menu:  # То создадим менюшку если она еще не существует
                nuke.pluginAddPath(f"{gizmos_folder}/{gp_name}/{name}")  # Добавляем папку в plugin path чтобы можно было вызывать nuke.createNode('some_name.gizmo')
                module_name = f'{name}.menu'
                if module_name in sys.modules:
                    importlib.reload(sys.modules[module_name])  # Менюшку уже создавали, нужно пересоздать
                else:
                    try:
                        importlib.import_module(module_name)  # Импортируем если никогда не был импортирован(т.е. менюшка до этого не была создана вызовом menu)
                    except:
                        pass
        else:  # Если пользователь выключил плагин(или он был выключен)
            if pack_menu:  # Тогда удалим менюшку если она существует
                nuke.menu('Nodes').menu(gp_name).removeItem(name)

    name = "ComfyUI"
    comfy_menu = nuke.menu("Nodes").findItem(name)
    if panel.knDict.get(name).value():  # Если пользователь включил плагин(или он был включен)
        if not comfy_menu:  # То создадим менюшку если она еще не существует
            nuke.pluginAddPath(f"{gizmos_folder}/{name}Nuke")  # Добавляем папку в plugin path чтобы можно было вызывать nuke.createNode()
            nuke.pluginAddPath(f"{gizmos_folder}/{name}Nuke/Workflows")  # Добавляем папку Workflows хотя она добавляется в menu.py(возможно там нужно указывать полный путь)
            module_name = f'{name}Nuke.menu'
            if module_name in sys.modules:
                importlib.reload(sys.modules[module_name])  # Менюшку уже создавали, нужно пересоздать
            else:
                try:
                    importlib.import_module(module_name)  # Импортируем если никогда не был импортирован(т.е. менюшка до этого не была создана вызовом menu)
                except:
                    pass
    else:
        if comfy_menu:  # Тогда удалим менюшку если она существует
            nuke.menu('Nodes').removeItem(name)

def getGPmenu() -> nuke.Menu:
    """
    Вернет меню для GizmoPacks. Если такого меню не существует, то создаст его
    """
    pack = nuke.menu('Nodes').menu(gp_name)
    if not pack:
        pack = nuke.menu('Nodes').addMenu(gp_name, icon=gp_name+'.png')
    return pack
