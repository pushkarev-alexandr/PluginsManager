#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#created by: Pushkarev Aleksandr

import os, json

json_path = os.path.dirname(__file__).replace('\\','/')+'/pluginsManager.json'  # Файл с настройками пользователей

def main():
    if os.path.isfile(json_path):
        name = input('Какой плагин выставляем(регистр важен): ')
        value = input('Значение (true/false можно маленькими): ')
        if value.lower() in ['true','false']:
            with open(json_path,'r') as f:
                json_data = json.load(f)
            for user in json_data:
                prev_value = json_data[user].get(name)
                new_value = value.lower()=='true'
                json_data[user][name] = new_value
                print(f'{user} {prev_value}->{new_value}')
            with open(json_path,'w') as f:  # Записываем эти изменения в файл
                json.dump(json_data, f, indent=4)
        else:
            print('Неправильное значение')
    else:
        print(f'Нет файла {json_path}')

if __name__ == "__main__":
    main()