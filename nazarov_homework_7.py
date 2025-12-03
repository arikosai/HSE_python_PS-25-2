# cоздадим класс Client для удобства хранения данных
class Client:
    def __init__(self, name, device_type, browser, sex, age, bill, region):
        # в csv файле некоторые имена взяты в кавычки, так как внутри имени тоже используются кавычки
        # чтобы не выводить лишние кавычки их нужно удалить
        if name.startswith('"'):
            name = name[1:-1] # убираем кавычки из начала и конца
            self.name = name.replace('""', '"') # убираем дублирующие кавычки
        else:
            self.name = name

        self.device_type = device_type
        self.browser = browser
        self.sex = sex
        self.age = age
        self.bill = bill
        self.region = region


with open("web_clients_correct.csv", 'r') as file_in, open("web_clients.txt", 'w') as file_out:
    headings = file_in.readline() # считываем первую строку с заголовками

    for line in file_in:
        line = line.strip()
        line_split = line.split(',')
        person = Client(*line_split)

        if person.sex == 'male':
            sex = 'мужского'
            sex_verb = 'совершил'
        else:
            sex = 'женского'
            sex_verb = 'совершила'

        if person.device_type == 'mobile':
            device = 'мобильного'
        elif person.device_type == 'desktop':
            device = 'компьютера'
        elif person.device_type == 'tablet':
            device = 'планшета'
        else:
            device = 'ноутбука'

        if person.region == '-':
            region = 'неизвестен'
        else:
            region = person.region

        print(
            f'Пользователь {person.name} {sex} пола, '
            f'{person.age} лет {sex_verb} покупку на {person.bill} у.е. '
            f'с {device} из браузера {person.browser}. '
            f'Регион, из которого совершалась покупка: {region}.',
            file=file_out
        )
