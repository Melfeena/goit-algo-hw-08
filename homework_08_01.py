from collections import UserDict
from datetime import datetime as dt
from datetime import timedelta
import pickle


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please. Or old and new phone, if You want to change the old phone"
        except TypeError:
            return "Wrong type of data"
        except KeyError:
            return "Wrong key value"
        except IndexError:
            return "Enter the argument for the command"
        except Exception as Error:
            return f"Error: {Error}"
    return inner

class PhoneLengthError(Exception):
     def __init__(self, message="Phone length is not according to requirements"):
          self.message=message
          super().__init__(self.message)

class PhoneFormatError(Exception):
     def __init__(self, message="Phone length is not according to requirements"):
          self.message=message
          super().__init__(self.message)


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Birthday(Field):
    def validate(self):
        try:
            birthday=dt.strptime(self, "%d.%m.%Y")
        except ValueError:
            raise ValueError
        return str((dt.strftime(birthday, "%d.%m.%Y")))    
        

class Name(Field):
    # реалізація класу
		pass

class Phone(Field):
    def chek_format(self):
        if len(self)!=10: 
            raise PhoneLengthError("Phone length shall be 10 digits")
        elif  not self.isnumeric():
            raise PhoneFormatError("Phone shall consist only digits")
        else:
            return self
   
class Record: 
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday= None

    def add_phone(self,phone):
        try:
             self.phones.append((Phone.chek_format(phone)))
        except Exception as e:
             print(e)

    def __str__(self):
        string=f"Contact name: {self.name.value}, phones: {'; '.join(p for p in self.phones)}"
        if (self.birthday):
            string+=f", Birthday: {self.birthday}"
        return string
    
    def edit_phone(self,old,new):
        if old in self.phones:
            self.phones.remove(old)
            try:
                self.phones.append(str(Phone.chek_format(new)))
            except Exception as e:
                print(e)

    def find_phone(self,phone):
         if phone in self.phones:
            print(f"The phone is in the list {phone}")
            return phone
         else: None #return f"This phone was not found for {self.name}"
    
    def remove_phone(self,phone):
        if phone in self.phones:
            self.phones.remove(phone)   

    def add_birthday(self,birthday):
         self.birthday=Birthday.validate(birthday)

    def show_birthday(self):
        return self.birthday
    


class AddressBook(UserDict):#Список [], в якому є записи. Запис містить Ім'я, телефони
    def add_record(self,item:Record):
          self.data[item.name.value]=item

    def find(self,item:Record)->Record:
         return self.data.get(item)
         
    def delete(self,item:Record):
         if item in self.data:
              del self.data[item]

    @input_error
    def get_upcoming_birthdays(self):
        self.next_W_bdays={}
        for name,record in self.data.items():
            if record.show_birthday():
                person_birthday=record.show_birthday()
        
                birthday=dt.strptime(person_birthday, "%d.%m.%Y").date()            
                current_date=dt.now().date()
                #change year to current year
                birthday_sel=birthday.replace(year=current_date.year)
                #if selebration is in past change to next year
                if birthday_sel<current_date:
                    birthday_sel=birthday.replace(year=(current_date.year+1))
                # check if the birthday in next 7 days
                age = current_date.year-birthday.year
                if ((current_date+timedelta(days=7))>birthday_sel):
                    self.next_W_bdays[name]=[birthday_sel.strftime("%d.%m.%Y"),birthday_sel.strftime("%a"),age]
        return self.next_W_bdays
    
@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    print(phone)
    return message

@input_error
def change_contact(args, book:AddressBook):
    name,old_phone,new_phone,*_=args
    record= book.find(name)
    message = "Fhone updated."
    print(name)
    print(old_phone)
    print(new_phone)
    if record is None:
        message = "Nos such contact found."
    elif record.find_phone(old_phone):
        record.edit_phone(old_phone,new_phone)
        message=f"Old phone {old_phone} was updated to new phone {new_phone}"
    else:
        record.add_phone(new_phone)
        message=f"Old phone was not found, the new phone {new_phone} is added to contact"
    return message

@input_error
def show_phone(args, book:AddressBook):
    name,*_=args
    record=book.find(name)
    pho=""
    for phone in record.phones:
        pho += f"{phone} "
    return f"Phone number(s) of the {name} are {pho.strip()}." 

@input_error
def show_all_contacts(book:AddressBook):
    for name, record in book.data.items():
       print(record)

@input_error
def add_birthday_contact(args,book:AddressBook):
    name, birthday,*_=args
    record=book.find(name)
    record.add_birthday(birthday)
    return "Birthday added"

@input_error
def show_birthday_contact(args,book:AddressBook):
    name,*_=args
    record=book.find(name)
    return f"{name} has his birthday on {record.show_birthday()}"

@input_error
def when_party(book:AddressBook):
    birthdays = book.get_upcoming_birthdays()
    # birthdays={'John': ['11.03.2024', 'Mon', 34]}
    if birthdays:
        # print(birthdays)
        for key, value in birthdays.items():
            print(f"{key} has his party on next {value[1]}, {value[0]} and he will be {value[2]} years")


def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()
    
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)
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
            show_all_contacts(book)

        elif command == "add-birthday":
            print(add_birthday_contact(args,book))

        elif command == "show-birthday":
            print(show_birthday_contact(args,book))

        elif command == "birthdays":
            when_party(book)

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()    