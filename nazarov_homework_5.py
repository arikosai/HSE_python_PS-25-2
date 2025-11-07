from datetime import datetime


formats = {
    "The Moscow Times": "%A, %B %d, %Y",
    "The Guardian": "%A, %d.%m.%y",
    "Daily News": "%A, %d %B %Y"
}

print("Введите название газеты и дату в нужном формате.")
print("Доступные газеты: The Moscow Times, The Guardian, Daily News")
print("Для выхода введите 'q'.")
print()

while True:
    newspaper = input("Введите название газеты:\n")
    if newspaper == 'q':
        print("Программа завершена.")
        break

    if newspaper not in formats:
        print("Неизвестная газета. Попробуйте снова.")

    date_str = input("Введите дату:\n")
    if date_str == 'q':
        print("Программа завершена.")
        break

    try:
        date_obj = datetime.strptime(date_str, formats[newspaper])
        print(f"Дата в объекте datetime: {date_obj}\n")
    except ValueError:
        print("Ошибка: введённая дата не соответствует формату данной газеты.")
        print("Попробуйте снова.\n")
        continue
