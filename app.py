from tqdm import tqdm
import language_tool_python
import requests
import os
import json
import time


def loading():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Загрузка...")


loading()
error = ""
tool = language_tool_python.LanguageTool('ru-RU')


# standard_data = {"language": "ru-RU", "service": "lgt"}


"""
Внесены изменения
- в 86-90 строки match.py
- в 73 строку utils.py
"""


def services():
    pass


def language():
    pass


def settings():
    global error
    while True:
        error_func()
        print("Настройки")
        print('"\033[33m--language\033[37m" Язык')
        print('"\033[33m--service\033[37m" Выбор сервиса')
        print('"\033[33m--back\033[37m" Назад')
        print('"\033[33m--EXIT\033[37m" Выход')
        command = input("Введите команду: ")
        os.system('cls' if os.name == 'nt' else 'clear')
        if command == "--language":
            language()
        elif command == "--service":
            services()
        elif command == "--back":
            return
        elif command == "--EXIT":
            exit()
        else:
            error = "Неверная команда"


def save_file(matches, text, mask, path, count_text, correct_text, service):
    if service == "lgt":
        json_text = json.loads(json.dumps([match.__dict__ for match in matches]))
    else:
        json_text = matches
    if not path:
        name_file = time.strftime("%m.%d.%y_%H.%M.%S", time.localtime())
    else:
        name_file = path + "/Text " + count_text
    os.mkdir(name_file)
    with open(name_file + "/matches.txt", 'w', encoding="UTF-8") as outfile:
        json.dump(json_text, outfile, sort_keys=True, indent=4, ensure_ascii=False)
    with open(name_file + "/input_text.txt", 'a', encoding="UTF-8") as outfile:
        for i in range(len(text)):
            if mask[i] == 1:
                outfile.write("{" + text[i])
            elif mask[i] == -1:
                outfile.write("}" + text[i])
            else:
                outfile.write(text[i])
    with open(name_file + "/correct_text.txt", 'w', encoding="UTF-8") as outfile:
        outfile.write(correct_text)


def save_all(folder, all_files, service):
    name_file = time.strftime("%m.%d.%y_%H.%M.%S", time.localtime())
    os.mkdir(name_file)
    for i in tqdm(range(len(all_files))):
        with open(folder + "/" + all_files[i], mode="r", encoding="UTF-8") as file:
            text = file.read()
        if service == "lgt":
            matches = tool.check(text)
            correct_text = tool.correct(text)
            mask = [0 for _ in range(len(text))]
            for match in matches:
                mask[match.offset] = 1
                mask[match.offset + match.errorLength] = -1
        else:
            _, matches, text, mask, correct_text = check_text_Yandex_small(text, "_")
        save_file(matches, text, mask, name_file, all_files[i], correct_text, service)
    os.system('cls' if os.name == 'nt' else 'clear')
    print('\033[33mУспешное сохранение\033[37m')


def error_func():
    global error
    if error != "":
        print("\033[31m{}\033[37m".format(error))
        error = ""


def func_check_text(filename, matches, text, mask, correct_text, service):
    global error
    print_open_file(filename)
    while True:
        error_func()
        command = input("Введите команду: ")
        if command == "--save":
            save_file(matches, text, mask, "", 0, correct_text, service)
        elif command == "--count":
            print("Колличество ошибок в тексте: " + str(len(matches)))
        elif command == "--print":
            print(text)
        elif command == "--print_error":
            count = 0
            for i in range(len(text)):
                count += mask[i]
                if count > 0:
                    print("\033[31m{}\033[37m".format(text[i]), end="")
                else:
                    print(text[i], end="")
            print()
        elif command == "--print_correct":
            print(correct_text)
        elif command == "--clear":
            os.system('cls' if os.name == 'nt' else 'clear')
            print_open_file(filename)
        elif command == "--back":
            os.system('cls' if os.name == 'nt' else 'clear')
            return
        elif command == "--EXIT":
            os.system('cls' if os.name == 'nt' else 'clear')
            exit()
        else:
            error = "Неверная команда"


def print_open_file(filename):
    print("Открыт файл " + "\033[33m {}\033[37m".format(filename.split("/")[-1]))
    print("Команды для работы:")
    print('"\033[33m--save\033[37m" Сохранить информацию в файле')
    print('"\033[33m--count\033[37m" Вывести колличество найденных ошибок в тексте')
    print('"\033[33m--print\033[37m" Вывести текст из файла')
    print('"\033[33m--print_error\033[37m" Вывести текст с выделенными ошибками')
    print('"\033[33m--print_correct\033[37m" Вывести исправленный текст')
    print('"\033[33m--clear\033[37m" Очистить консоль')
    print('"\033[33m--back\033[37m" Назад')
    print('"\033[33m--EXIT\033[37m" Выход')


def check_text_lgt(text, filename):
    loading()
    matches = tool.check(text)
    mask = [0 for _ in range(len(text))]
    for match in matches:
        mask[match.offset] = 1
        mask[match.offset + match.errorLength] = -1
    correct_text = tool.correct(text)
    return filename, matches, text, mask, correct_text


def check_text_Yandex_small(text, filename):
    response = requests.get('https://speller.yandex.net/services/spellservice.json/checkText', params={'text': text, 'lang': 'ru'})
    matches = json.loads(response.text)
    mask = [0 for _ in range(len(text))]
    dict_matches = dict()
    correct_text = list()
    for match in matches:
        dict_matches[match['pos']] = [match['len'], match['s'][0]]
        mask[match['pos']] = 1
        mask[match['pos'] + match['len']] = -1
    flag = 0
    for i in range(len(text)):
        if mask[i] == 1:
            flag = 1
            correct_text.append(dict_matches[i][1])
        elif mask[i] == -1:
            flag = 0
            correct_text.append(text[i])
        elif flag == 0:
            correct_text.append(text[i])
    correct_text = "".join(correct_text)
    return filename, matches, text, mask, correct_text


def open_file_folders(path, filename):
    global error
    try:
        file = open(path + "/" + filename, mode='r', encoding="UTF-8")
    except FileNotFoundError:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\033[31m{}\033[37m".format("Файл не найден"))
        return
    text = file.read()
    return text, filename


def open_file():
    global error
    path = input("Введите путь до файла: ")
    path = path.replace("\\", "/")
    try:
        file = open(path, mode="r", encoding="UTF-8")
    except FileNotFoundError:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\033[31m{}\033[37m".format("Файл не найден"))
        return
    text = file.read()
    os.system('cls' if os.name == 'nt' else 'clear')
    arg = func_service()
    if arg == "yandex":
        func_check_text(*check_text_Yandex_small(text, ""), arg)
    else:
        func_check_text(*check_text_lgt(text, ""), arg)


def open_folder():
    global error
    folder = input("Введите путь до папки: ")
    folder = folder.replace("\\", "/")
    try:
        all_files = list(filter(lambda x: x[-4:] == '.txt', os.listdir(folder)))
    except FileNotFoundError:
        os.system('cls' if os.name == 'nt' else 'clear')
        error = "Файл или папка не найдены"
        return
    os.system('cls' if os.name == 'nt' else 'clear')
    return folder, all_files


def func_service():
    global error
    print("Сервисы для проверки: ")
    print('"\033[33m--yandex\033[37m" Проверка через Yandex Speller')
    print('"\033[33m--lgt\033[37m" Проверка через LanguageTool')
    folder = input("Выберите сервис: ")
    os.system('cls' if os.name == 'nt' else 'clear')
    if folder == "--lgt":
        return "lgt"
    elif folder == "--yandex":
        return "yandex"
    else:
        error = "Вы ввели неверный сервис для проверки. Выбран Yandex"
        return "yandex"


def func_folder(folder, all_files):
    global error
    while True:
        error_func()
        print("Папка \033[33m{}\033[37m открыта: ".format(folder.split("/")[-1]))
        for file in all_files:
            print("\033[33m{}\033[37m".format(file))
        print("Команды для работы:")
        print('"\033[33m--saveALL\033[37m" Сохранить все ошибки во всех файлах')
        print('"\033[33m--{name_file}\033[37m" Открыть файл')
        print('"\033[33m--back\033[37m" Назад')
        print('"\033[33m--EXIT\033[37m" Выход')
        command = input("Введите команду: ")
        os.system('cls' if os.name == 'nt' else 'clear')
        if command == "--saveALL":
            arg = func_service()
            save_all(folder, all_files, arg)
            return
        elif command[2:] in all_files:
            d = open_file_folders(folder, command[2:])
            if d:
                arg = func_service()
                if arg == "yandex":
                    func_check_text(*check_text_Yandex_small(*d), arg)
                else:
                    func_check_text(*check_text_lgt(*d), arg)
        elif command == "--back":
            return
        elif command == "--EXIT":
            exit()
        else:
            error = "Неверная команда"


def main():
    global error
    while True:
        error_func()
        print("Команды для работы:")
        print('"\033[33m--file\033[37m" Проверить файл')
        print('"\033[33m--folder\033[37m" Проверить папку файлов')
        print('"\033[33m--settings\033[37m" Открыть настройки // В разработке')
        print('"\033[33m--info\033[37m" Информация //В разработке')
        print('"\033[33m--exit\033[37m" Выход')
        command = input("Введите команду: ")
        os.system('cls' if os.name == 'nt' else 'clear')
        if command == "--settings":
            settings()
        elif command == "--file":
            open_file()
        elif command == "--folder":
            arg = open_folder()
            if arg:
                func_folder(*arg)
        elif command == "--info":
            pass
        elif command == "--exit":
            exit()
        else:
            error = "Неверная команда"


if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    main()
