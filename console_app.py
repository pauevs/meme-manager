from models import Meme, TextMeme, ImageMeme, VideoMeme


def show_menu():
    print("\n=== Meme Manager (консоль) ===")
    print("1. Добавить новый элемент")
    print("2. Удалить элемент по индексу")
    print("3. Вывести все элементы")
    print("4. Сравнить два элемента по индексам")
    print("5. Выход")


def add_element(collection):
    print("\nВыберите тип мема:")
    print("1 - TextMeme (текстовый)")
    print("2 - ImageMeme (картинка)")
    print("3 - VideoMeme (видео)")
    choice = input("Ваш выбор (1/2/3): ").strip()
    try:
        title = input("Название: ").strip()
        description = input("Описание: ").strip()
        if choice == "1":
            text_content = input("Текст: ").strip()
            font_size = int(input("Размер шрифта (8-72): "))
            item = TextMeme(title=title, description=description,
                            text_content=text_content, font_size=font_size)
        elif choice == "2":
            image_path = input("Путь к картинке: ").strip()
            width = int(input("Ширина в пикселях (50-4000): "))
            item = ImageMeme(title=title, description=description,
                             image_path=image_path, width=width)
        elif choice == "3":
            video_path = input("Путь к видео: ").strip()
            duration = int(input("Длительность в секундах (1-600): "))
            item = VideoMeme(title=title, description=description,
                             video_path=video_path, duration_sec=duration)
        else:
            print("Неизвестный тип. Возврат в меню.")
            return
        collection.append(item)
        print("Добавлено:", repr(item))
    except ValueError as e:
        print("Ошибка ввода:", e)


def remove_element(collection):
    if not collection:
        print("Коллекция пуста.")
        return
    try:
        idx = int(input("Индекс для удаления: "))
        if 0 <= idx < len(collection):
            removed = collection.pop(idx)
            print("Удалено:", repr(removed))
        else:
            print("Индекс вне диапазона.")
    except ValueError:
        print("Введите целое число.")


def print_all(collection):
    if not collection:
        print("Коллекция пуста.")
        return
    print("\nВсего элементов:", len(collection))
    for i, item in enumerate(collection):
        print("  [" + str(i) + "]", repr(item))


def compare_two(collection):
    if len(collection) < 2:
        print("Нужно минимум 2 элемента для сравнения.")
        return
    try:
        i = int(input("Первый индекс: "))
        j = int(input("Второй индекс: "))
        if not (0 <= i < len(collection) and 0 <= j < len(collection)):
            print("Неверные индексы.")
            return
        if collection[i] == collection[j]:
            print("Элементы РАВНЫ.")
        else:
            print("Элементы НЕ равны.")
    except ValueError:
        print("Введите целые числа.")


def main():
    collection = []
    while True:
        show_menu()
        choice = input("Ваш выбор: ").strip()
        if choice == "1":
            add_element(collection)
        elif choice == "2":
            remove_element(collection)
        elif choice == "3":
            print_all(collection)
        elif choice == "4":
            compare_two(collection)
        elif choice == "5":
            print("До свидания!")
            break
        else:
            print("Неизвестная команда. Попробуйте снова.")


if __name__ == "__main__":
    main()