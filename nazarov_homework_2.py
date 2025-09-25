word = input("Введите слово: ")
length = len(word)
middle = length // 2

if length % 2 == 0:
    print(word[middle - 1:middle + 1])
else:
    print(word[middle])
