#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#created by: Pushkarev Aleksandr

import nuke, nukescripts
import os, json, getpass, re, importlib, sys

gp_name = 'GizmoPacks'  # Имя папки и менюшки для гизмо паков(должна совпадать с именем папки Z:\Nuke_Workgroup\gizmos\GizmoPacks)

curDir = os.path.dirname(__file__).replace("\\","/")  # Текущая папка
json_path = curDir+'/pluginsManager.json'  # Файл с настройками пользователей

# Типы плагинов, эти имена будут использоваться в менюшке
plTypes = ['Plugins','OFX','Gizmo Packs','Gizmos']

# имя кноба, лэйбл кноба, значение по умолчанию, можно ли редактировать значение
pluginsInfo = [['3DE4','3DE4 Lens Distortion',True,False],
['KeenTools','KeenTools',True,True],
['dcraw','Поддержка .CR2 файлов',False,True],
['NNFlowVector','NNFlowVector',True,True],
['OIDN','Open Image Denoise',False,True],
['OpticalFlares','Optical Flares',True,True]]

ofxInfo = [['NeatVideo','Neat Video',True,False],
['Frischluft','Frischluft',True,True],
['RE_Vision','RE:Vision',True,True],
['Tinderbox','Tinderbox',True,True],
['MochaPro2024','MochaPro',True,True],
['Sapphire','Sapphire',True,True],
['Continuum','Continuum',True,True]]

gizmoPacksInfo = [['AdrianPueyo','Adrian Pueyo',True,True],
['AitorEcheveste','Aitor Echeveste',True,True],
['Awesome3000','Awesome3000',True,True],
['BenMcEwan','BenMcEwan',True,True],
['Buddy','Buddy',False,True],
['CompositingAcademy','Compositing Academy',False,True],
['ExpressionNodes','Expression Nodes',False,True],
['DUCK','DUCK',False,True],
['LumaPictures','Luma Pictures',False,True],
['NukeSurvivalToolkit','Nuke Survival Toolkit',True,True],
['ParticlesCollection','ParticlesCollection',True,True],
['Pixelfudger','Pixelfudger',True,True],
['PointRender','Point Render',False,True],
['SPIN','SPIN',True,True],
['TX','TX',True,True]]

gizmoInfo = [['NukeDiffusion','Nuke Diffusion',False,True]]

allInfo = [pluginsInfo,ofxInfo,gizmoPacksInfo,gizmoInfo]

# Проверяет доступен ли плагин в текущей версии нюка
def isPluginAvailable(plugin_name):
    dll_plugins = os.path.normpath(os.path.join(curDir,"..","..","plugins/dll_plugins")).replace("\\","/")  # Папка с dll плагинами, которые зависят от версии нюка
    plugin_folder = f"{dll_plugins}/{plugin_name}"  # Папка конкретного плагина
    if not os.path.isdir(plugin_folder):  # Если папки нет, значит плагин точно не доступен
        return False
    nuke_ver_lst = [f for f in os.listdir(plugin_folder) if re.fullmatch(r"Nuke\d+\.\d+",f) and os.path.isdir(f"{plugin_folder}/{f}")]  # Получаем список папок Nuke##.#
    if not nuke_ver_lst:  # Если версий нет, значит безверсионный плагин, значит доступен
        return True
    elif f"Nuke{nuke.NUKE_VERSION_MAJOR}.{nuke.NUKE_VERSION_MINOR}" in nuke_ver_lst:  # Иначе проверяем есть ли плагин для текущей версии
        return True
    else:
        return False 

class SettingsPanel(nukescripts.PythonPanel):
    def __init__(self,json_data):
        nukescripts.PythonPanel.__init__(self,'Plugins Manager')
        self.setMinimumSize(350,760)

        user_settings = json_data.get(getpass.getuser())  # Получаем настройки плагинов для пользователя
        self.knDict = {}  # Коллектим все добавленные кнобы в виде словаря
        for j,plType in enumerate(plTypes):  # Проходимся по типам Plugins, OFX, Gizmos
            self.addKnob(nuke.Text_Knob(plType.replace(' ','_'),plType+':'))  # Подпись для типов
            for i,inf in enumerate(allInfo[j]):  # Проходимся по списку плагинов для конкретного типа
                available =  [' (недоступен)',''][isPluginAvailable(inf[0]) or plType!='Plugins']  # Проверяем доступен ли плагин, если плагин не доступен в текущей версии, делаем пометку
                kn = nuke.Boolean_Knob(inf[0],inf[1]+available,inf[2])  # Создаем чекбокс с дефолтным значением
                if user_settings and user_settings.get(inf[0])!=None:  # Если для пользователя есть настройки, то заменим на пользовательские настройки
                    kn.setValue(user_settings.get(inf[0]))
                if not inf[3]:  # Делаем кноб недоступным для редактирования для 3DE4 и NeatVideo
                    kn.setEnabled(False)
                if i!=0:  # Если кноб не первый, то начнем с новой строки, чтобы кнобы чекбоксы были друг под другом
                    kn.setFlag(nuke.STARTLINE)
                self.knDict[inf[0]] = kn  # Добавляем кноб в словарь чтобы можно было позже получить к нему доступ
                self.addKnob(kn)

def pluginsManager():
    if not os.path.isfile(json_path):  # Если файла не существует создадим его и запишем в него пустой словарь
        with open(json_path,"w") as f:
            f.write("{}")
    
    # Читаем настройки из pluginsManager.json
    with open(json_path,"r") as f:
        json_data = json.load(f)
    
    panel = SettingsPanel(json_data)
    if not panel.showModalDialog():
        return

    json_data[getpass.getuser()] = {}  # Записываем в словарь настройки отмеченные пользователем
    for lst in allInfo:
        for i in lst:
            json_data[getpass.getuser()][i[0]] = panel.knDict.get(i[0]).value()
    
    with open(json_path,'w') as f:  # Записываем эти изменения в файл
        json.dump(json_data, f, indent=4)

    gp_folder = os.path.normpath(os.path.join(curDir,"..","..","gizmos",gp_name)).replace("\\","/")  # Папка со всеми паками гизм
    for name in gizmoPacksInfo:  # Проходимся по всем пакам
        name = name[0]  # Берем имя пака
        pack_menu = nuke.menu('Nodes').menu(f'{gp_name}/{name}')  # Ищем менюшку
        if panel.knDict.get(name).value():#если пользователь включил плагин(или он был включен)
            if not pack_menu:  # То создадим менюшку если она еще не существует
                nuke.pluginAddPath(f"{gp_folder}/{name}")  # Добавляем папку в plugin path чтобы можно было вызывать nuke.createNode('some_name.gizmo')
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

def getGPmenu() -> nuke.Menu:
    """
    Вернет меню для GizmoPacks. Если такого меню не существует, то создаст его
    """
    pack = nuke.menu('Nodes').menu(gp_name)
    if not pack:
        pack = nuke.menu('Nodes').addMenu(gp_name, icon=gp_name+'.png')
    return pack