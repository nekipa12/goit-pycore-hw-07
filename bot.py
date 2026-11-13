from functools import wraps

from address_book import AddressBook, Record


def input_error(func):
    """Декоратор: перетворює помилки введення на зрозумілі відповіді."""
    @wraps(func)
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as error:
            # текст помилки вже зрозумілий: його формують перевірки
            # аргументів в обробниках і класи Phone та Birthday
            return str(error)
        except KeyError:
            # контакту з таким ім'ям у книзі немає
            return "Contact not found."

    return inner


def parse_input(user_input: str) -> tuple:
    """Розбиває рядок на команду (у нижньому регістрі) та аргументи."""
    parts = user_input.split()
    if not parts:
        return ("",)
    command = parts[0].lower()
    return (command, *parts[1:])


@input_error
def add_contact(args: list, book: AddressBook) -> str:
    """add [ім'я] [телефон]: новий контакт або ще один номер до наявного."""
    if len(args) < 2:
        raise ValueError("Usage: add [name] [phone]")
    name, phone, *_ = args
    record = book.find(name)
    if record is None:
        # спочатку додаємо номер і лише потім кладемо запис у книгу:
        # якщо номер некоректний, порожній контакт не з'явиться
        record = Record(name)
        record.add_phone(phone)
        book.add_record(record)
        return "Contact added."
    record.add_phone(phone)
    return "Contact updated."


@input_error
def change_contact(args: list, book: AddressBook) -> str:
    """change [ім'я] [старий телефон] [новий телефон]: заміна номера."""
    if len(args) < 3:
        raise ValueError("Usage: change [name] [old phone] [new phone]")
    name, old_phone, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError(name)
    record.edit_phone(old_phone, new_phone)
    return "Contact updated."


@input_error
def show_phone(args: list, book: AddressBook) -> str:
    """phone [ім'я]: усі телефони контакту."""
    if len(args) < 1:
        raise ValueError("Usage: phone [name]")
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError(name)
    if not record.phones:
        return f"{name} has no phones."
    return f"{name}: {'; '.join(p.value for p in record.phones)}"


def show_all(book: AddressBook) -> str:
    """all: усі контакти книги."""
    if not book.data:
        return "No contacts saved yet."
    return str(book)


@input_error
def add_birthday(args: list, book: AddressBook) -> str:
    """add-birthday [ім'я] [DD.MM.YYYY]: додає день народження."""
    if len(args) < 2:
        raise ValueError("Usage: add-birthday [name] [DD.MM.YYYY]")
    name, birthday, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError(name)
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args: list, book: AddressBook) -> str:
    """show-birthday [ім'я]: показує день народження контакту."""
    if len(args) < 1:
        raise ValueError("Usage: show-birthday [name]")
    name = args[0]
    record = book.find(name)
    if record is None:
        raise KeyError(name)
    if record.birthday is None:
        return f"{name} has no birthday set."
    return f"{name}: {record.birthday}"


@input_error
def birthdays(args: list, book: AddressBook) -> str:
    """birthdays: кого вітати протягом наступного тижня."""
    upcoming = book.get_upcoming_birthdays()
    if not upcoming:
        return "No birthdays in the next 7 days."
    lines = []
    for item in upcoming:
        day = item["congratulation_date"].strftime("%d.%m.%Y, %A")
        lines.append(f"{day}: {item['name']}")
    return "\n".join(lines)


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)
        if not command:
            continue

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C або Ctrl+D: завершуємо роботу без traceback
        print("\nGood bye!")
