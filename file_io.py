import csv
import json
import os
from datetime import datetime

from openpyxl import Workbook, load_workbook

from models import Suit, Customer, Rental


def _date_to_str(value):
    if isinstance(value, datetime):
        return value.strftime('%Y.%m.%d')
    return value


def _parse_date(value):
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    for fmt in ('%Y.%m.%d', '%Y-%m-%d', '%Y-%m-%d %H:%M:%S'):
        try:
            return datetime.strptime(text[:19] if ' ' in text else text, fmt)
        except ValueError:
            continue
    raise ValueError(f'Bad date: {value}')


def write_suits(suits: list[Suit], path: str, file_name: str = "suits.csv") -> None:
    with open(os.path.join(path, file_name if file_name is not None else "suits.csv"), "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for suit in suits:
            writer.writerow([suit.id, suit.brand, suit.style, suit.size, suit.color, suit.cost_category_id])


def read_suits(path: str, file_name: str = "suits.csv", delimiter: str = ",") -> list[Suit]:
    with open(os.path.join(path, file_name if file_name is not None else "suits.csv"), "r", encoding="utf-8") as file:
        rows = csv.reader(file, delimiter=delimiter)
        return [
            Suit(int(row[0]), row[1], row[2], int(row[3]), row[4], int(row[5]))
            for row in rows if row and row[0] != "id"
        ]


def write_customers(customers: list[Customer], path: str, file_name: str = "customers.csv") -> None:
    with open(os.path.join(path, file_name if file_name is not None else "customers.csv"), "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for customer in customers:
            writer.writerow([
                customer.id,
                customer.first_name,
                customer.last_name,
                _date_to_str(customer.date_of_birth),
                customer.is_male,
                customer.phone,
            ])


def read_customers(path: str, file_name: str = "customers.csv", delimiter: str = ",") -> list[Customer]:
    with open(os.path.join(path, file_name if file_name is not None else "customers.csv"), "r", encoding="utf-8") as file:
        rows = csv.reader(file, delimiter=delimiter)
        return [
            Customer(int(row[0]), row[1], row[2], _parse_date(row[3]), int(row[4]), row[5])
            for row in rows if row and row[0] != "id"
        ]


def write_rentals(rentals: list[Rental], path: str, file_name: str = "rentals.csv") -> None:
    with open(os.path.join(path, file_name if file_name is not None else "rentals.csv"), "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        for rental in rentals:
            writer.writerow([
                rental.id,
                rental.suit_id,
                rental.customer_id,
                _date_to_str(rental.rental_start),
                _date_to_str(rental.rental_end),
            ])


def read_rentals(path: str, file_name: str = "rentals.csv", delimiter: str = ",") -> list[Rental]:
    with open(os.path.join(path, file_name if file_name is not None else "rentals.csv"), "r", encoding="utf-8") as file:
        rows = csv.reader(file, delimiter=delimiter)
        return [
            Rental(int(row[0]), int(row[1]), int(row[2]), _parse_date(row[3]), _parse_date(row[4]))
            for row in rows if row and row[0] != "id"
        ]


def write_suits_json(suits: list[Suit], path: str, file_name: str = "suits.json") -> None:
    with open(os.path.join(path, file_name if file_name is not None else "suits.json"), "w", encoding="utf-8") as file:
        json.dump(
            [
                {
                    "id": suit.id,
                    "brand": suit.brand,
                    "style": suit.style,
                    "size": suit.size,
                    "color": suit.color,
                    "cost_category_id": suit.cost_category_id,
                }
                for suit in suits
            ],
            file,
            indent=2,
        )


def read_suits_json(path: str, file_name: str = "suits.json") -> list[Suit]:
    with open(os.path.join(path, file_name), "r", encoding="utf-8") as file:
        rows = json.load(file)
        if rows and isinstance(rows[0], dict):
            return [Suit(int(r["id"]), r["brand"], r["style"], int(r["size"]), r["color"], int(r["cost_category_id"])) for r in rows]
        return [Suit(int(row[0]), row[1], row[2], int(row[3]), row[4], int(row[5])) for row in rows]


def write_customers_json(customers: list[Customer], path: str, file_name: str = "customers.json") -> None:
    with open(os.path.join(path, file_name if file_name is not None else "customers.json"), "w", encoding="utf-8") as file:
        json.dump(
            [
                {
                    "id": c.id,
                    "first_name": c.first_name,
                    "last_name": c.last_name,
                    "date_of_birth": _date_to_str(c.date_of_birth),
                    "is_male": c.is_male,
                    "phone": c.phone,
                }
                for c in customers
            ],
            file,
            indent=2,
        )


def read_customers_json(path: str, file_name: str = "customers.json") -> list[Customer]:
    with open(os.path.join(path, file_name), "r", encoding="utf-8") as file:
        rows = json.load(file)
        if rows and isinstance(rows[0], dict):
            return [
                Customer(int(r["id"]), r["first_name"], r["last_name"], _parse_date(r["date_of_birth"]), int(r["is_male"]), r["phone"])
                for r in rows
            ]
        return [Customer(int(row[0]), row[1], row[2], _parse_date(row[3]), int(row[4]), row[5]) for row in rows]


def write_rentals_json(rentals: list[Rental], path: str, file_name: str = "rentals.json") -> None:
    with open(os.path.join(path, file_name if file_name is not None else "rentals.json"), "w", encoding="utf-8") as file:
        json.dump(
            [
                {
                    "id": r.id,
                    "suit_id": r.suit_id,
                    "customer_id": r.customer_id,
                    "rental_start": _date_to_str(r.rental_start),
                    "rental_end": _date_to_str(r.rental_end),
                }
                for r in rentals
            ],
            file,
            indent=2,
        )


def read_rentals_json(path: str, file_name: str = "rentals.json") -> list[Rental]:
    with open(os.path.join(path, file_name), "r", encoding="utf-8") as file:
        rows = json.load(file)
        if rows and isinstance(rows[0], dict):
            return [
                Rental(int(r["id"]), int(r["suit_id"]), int(r["customer_id"]), _parse_date(r["rental_start"]), _parse_date(r["rental_end"]))
                for r in rows
            ]
        return [Rental(int(row[0]), int(row[1]), int(row[2]), _parse_date(row[3]), _parse_date(row[4])) for row in rows]


def _write_excel(path, file_name, rows):
    book = Workbook()
    sheet = book.active
    for row in rows:
        sheet.append(row)
    book.save(os.path.join(path, file_name))


def _read_excel(path, file_name):
    sheet = load_workbook(os.path.join(path, file_name), data_only=True).active
    rows = []
    for row in sheet.iter_rows(values_only=True):
        if not row or row[0] in (None, "", "id"):
            continue
        rows.append(list(row))
    return rows


def write_suits_excel(suits: list[Suit], path: str, file_name: str = "suits.xlsx") -> None:
    _write_excel(path, file_name if file_name is not None else "suits.xlsx", [[suit.id, suit.brand, suit.style, suit.size, suit.color, suit.cost_category_id] for suit in suits])


def read_suits_excel(path: str, file_name: str = "suits.xlsx") -> list[Suit]:
    return [Suit(int(row[0]), row[1], row[2], int(row[3]), row[4], int(row[5])) for row in _read_excel(path, file_name)]


def write_customers_excel(customers: list[Customer], path: str, file_name: str = "customers.xlsx") -> None:
    _write_excel(path, file_name if file_name is not None else "customers.xlsx", [
        [c.id, c.first_name, c.last_name, _date_to_str(c.date_of_birth), c.is_male, c.phone]
        for c in customers
    ])


def read_customers_excel(path: str, file_name: str = "customers.xlsx") -> list[Customer]:
    return [Customer(int(row[0]), row[1], row[2], _parse_date(row[3]), int(row[4]), row[5]) for row in _read_excel(path, file_name)]


def write_rentals_excel(rentals: list[Rental], path: str, file_name: str = "rentals.xlsx") -> None:
    _write_excel(path, file_name if file_name is not None else "rentals.xlsx", [
        [r.id, r.suit_id, r.customer_id, _date_to_str(r.rental_start), _date_to_str(r.rental_end)]
        for r in rentals
    ])


def read_rentals_excel(path: str, file_name: str = "rentals.xlsx") -> list[Rental]:
    return [Rental(int(row[0]), int(row[1]), int(row[2]), _parse_date(row[3]), _parse_date(row[4])) for row in _read_excel(path, file_name)]
