from collections import UserDict
from datetime import datetime, date, timedelta


class Field:
    """Базовий клас для полів запису."""

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    """Ім'я контакту. Обов'язкове поле, порожнім бути не може."""

    def __init__(self, value):
        value = str(value).strip()
        if not value:
            raise ValueError("Name cannot be empty.")
        super().__init__(value)


class Phone(Field):
    """Номер телефону. Приймаємо тільки рядок рівно з 10 цифр."""

    def __init__(self, value):
        value = str(value).strip()
        if not (value.isdigit() and len(value) == 10):
            raise ValueError(
                f"Invalid phone number '{value}': "
                "must contain exactly 10 digits."
            )
        super().__init__(value)


class Birthday(Field):
    """День народження. Приймає рядок DD.MM.YYYY, зберігає об'єкт date."""

    def __init__(self, value):
        value = str(value).strip()
        try:
            birthday = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        if birthday > date.today():
            raise ValueError("Birthday cannot be in the future.")
        super().__init__(birthday)

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")


class Record:
    """Запис у книзі: ім'я, список телефонів і день народження."""

    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str):
        """Додає телефон до запису. Той самий номер двічі не додаємо."""
        if self.find_phone(phone) is not None:
            raise ValueError(f"Phone {phone} already exists.")
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str):
        """Видаляє телефон із запису."""
        phone_obj = self.find_phone(phone)
        if phone_obj is None:
            raise ValueError(f"Phone {phone} not found.")
        self.phones.remove(phone_obj)

    def edit_phone(self, old_phone: str, new_phone: str):
        """Замінює старий номер на новий."""
        phone_obj = self.find_phone(old_phone)
        if phone_obj is None:
            raise ValueError(f"Phone {old_phone} not found.")
        if new_phone != old_phone and self.find_phone(new_phone) is not None:
            raise ValueError(f"Phone {new_phone} already exists.")
        # якщо новий номер некоректний, Phone кине ValueError
        # і старий номер залишиться на місці
        new_phone_obj = Phone(new_phone)
        index = self.phones.index(phone_obj)
        self.phones[index] = new_phone_obj

    def find_phone(self, phone: str):
        """Повертає об'єкт Phone за номером або None, якщо такого немає."""
        for phone_obj in self.phones:
            if phone_obj.value == phone:
                return phone_obj
        return None

    def add_birthday(self, birthday: str):
        """Додає день народження. Воно одне, тому повторний виклик замінює."""
        self.birthday = Birthday(birthday)

    def __str__(self):
        phones = "; ".join(p.value for p in self.phones)
        result = f"Contact name: {self.name.value}, phones: {phones}"
        if self.birthday is not None:
            result += f", birthday: {self.birthday}"
        return result


def birthday_in_year(birthday: date, year: int) -> date:
    """День народження у вказаному році. 29 лютого святкуємо 1 березня."""
    try:
        return birthday.replace(year=year)
    except ValueError:
        return date(year, 3, 1)


class AddressBook(UserDict):
    """Книга контактів. Ключ - ім'я контакту, значення - об'єкт Record."""

    def add_record(self, record: Record):
        """Додає запис до книги."""
        name = record.name.value
        if name in self.data:
            raise ValueError(f"Contact {name} already exists.")
        self.data[name] = record

    def find(self, name: str):
        """Повертає запис за ім'ям або None, якщо контакту немає."""
        return self.data.get(name)

    def delete(self, name: str):
        """Видаляє запис за ім'ям."""
        if name not in self.data:
            raise KeyError(f"Contact {name} not found.")
        del self.data[name]

    def get_upcoming_birthdays(self, days: int = 7) -> list:
        """
        Повертає список контактів, яких треба привітати протягом
        наступних days днів (разом із сьогоднішнім). Якщо день народження
        випадає на вихідний, дата привітання переноситься на понеділок.
        """
        today = date.today()
        upcoming = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = record.birthday.value
            year = today.year
            birthday_this_year = birthday_in_year(birthday, year)
            if birthday_this_year < today:
                # цього року вже минув, дивимось наступний
                birthday_this_year = birthday_in_year(birthday, year + 1)

            if (birthday_this_year - today).days >= days:
                continue

            congratulation_date = birthday_this_year
            if congratulation_date.weekday() == 5:    # субота
                congratulation_date += timedelta(days=2)
            elif congratulation_date.weekday() == 6:  # неділя
                congratulation_date += timedelta(days=1)

            upcoming.append({
                "name": record.name.value,
                "congratulation_date": congratulation_date,
            })

        # сортуємо за датою привітання, щоб список читався як календар
        upcoming.sort(key=lambda item: item["congratulation_date"])
        return upcoming

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())
