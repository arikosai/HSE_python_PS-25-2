documents = [
 {'type': 'passport', 'number': '2207 876234', 'name': 'Василий Гупкин'},
 {'type': 'invoice', 'number': '11-2', 'name': 'Геннадий Покемонов'},
 {'type': 'insurance', 'number': '10006', 'name': 'Аристарх Павлов'}
 ]

directories = {
 '1': ['2207 876234', '11-2'],
 '2': ['10006'],
 '3': []
}

def get_doc_owner_by_number(doc_number, docs):
    """
    Возвращает имя владельца по номеру документа.
    Если документ не найден — возвращает None.
    """
    for doc in docs:
        if doc['number'] == doc_number:
            return doc['name']
    return None

def command_p(docs):
    """
    Обрабатывает команду 'p': запрос владельца по номеру документа.
    """
    doc_number = input("Введите номер документа:\n")
    owner = get_doc_owner_by_number(doc_number, docs)
    if owner:
        print(f"Владелец документа: {owner}\n")
    else:
        print("Владелец документа: владелец не найден.\n")

def main():
    """
    Основной цикл программы. Выполняется, пока пользователь не введёт 'q'.
    """
    while True:
        command = input("Введите команду:\n")

        if command == 'p':
            command_p(documents)
        elif command == 'q':
            break

if __name__ == "__main__":
    main()