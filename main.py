import datetime
import os
from sql import SqlHandler
from models import Suit, Customer, Rental, CostCategory, parse_data
from generator import generate_suits, generate_customers, generate_costcategories
from file_io import (
    write_suits, read_suits, write_customers, read_customers, write_rentals, read_rentals,
    write_suits_json, read_suits_json, write_customers_json, read_customers_json,
    write_rentals_json, read_rentals_json,
    write_suits_excel, read_suits_excel, write_customers_excel, read_customers_excel,
    write_rentals_excel, read_rentals_excel,
)


def generate_suits_and_customers_and_categories(num_of_suits, num_of_customers, male_ratio, category_distribution, customers_locale):
    num_of_suits = int(num_of_suits) if num_of_suits else None
    num_of_customers = int(num_of_customers) if num_of_customers else None
    male_ratio = float(male_ratio) if male_ratio else None
    cost_category_dist = [int(x) for x in category_distribution.split(',')] if category_distribution else None
    customers_locale = customers_locale if customers_locale else None

    sqlhandler.drop_all()
    sqlhandler.ensure_tables()

    suits = generate_suits(num_of_suits, cost_category_dist)
    sqlhandler.fill_suits(suits)

    customers = generate_customers(num_of_customers, male_ratio, customers_locale)
    sqlhandler.fill_customers(customers)

    categories = generate_costcategories()
    sqlhandler.fill_costcategories(categories)
    return {'status': 'success', 'message': f'Kész: {len(suits)} öltöny és {len(customers)} ügyfél.'}



def get_suits():
    return parse_data(sqlhandler.read_table('suits'), Suit)

def get_customers():
    return parse_data(sqlhandler.read_table('customers'), Customer)

def get_costcategories():
    return parse_data(sqlhandler.read_table('costcategories'), CostCategory)

def get_rentals():
    return parse_data(sqlhandler.read_table('rentals'), Rental)


def export_entity(entity, path, kind='csv', file_name=None):
    writers = {
        ('suits', 'csv'): write_suits,
        ('customers', 'csv'): write_customers,
        ('rentals', 'csv'): write_rentals,
        ('suits', 'json'): write_suits_json,
        ('customers', 'json'): write_customers_json,
        ('rentals', 'json'): write_rentals_json,
        ('suits', 'xlsx'): write_suits_excel,
        ('customers', 'xlsx'): write_customers_excel,
        ('rentals', 'xlsx'): write_rentals_excel,
    }
    getters = {
        'suits': get_suits,
        'customers': get_customers,
        'rentals': get_rentals,
    }
    writers[(entity, kind)](getters[entity](), path, file_name)
    saved = os.path.join(path, file_name) if file_name else path
    names = {'suits': 'Öltönyök', 'customers': 'Ügyfelek', 'rentals': 'Kölcsönzések'}
    return {'status': 'success', 'message': f'{names[entity]} mentve: {saved}'}


def import_entity(entity, path, kind='csv', file_name=None):
    readers = {
        ('suits', 'csv'): read_suits,
        ('customers', 'csv'): read_customers,
        ('rentals', 'csv'): read_rentals,
        ('suits', 'json'): read_suits_json,
        ('customers', 'json'): read_customers_json,
        ('rentals', 'json'): read_rentals_json,
        ('suits', 'xlsx'): read_suits_excel,
        ('customers', 'xlsx'): read_customers_excel,
        ('rentals', 'xlsx'): read_rentals_excel,
    }
    fillers = {
        'suits': sqlhandler.fill_suits,
        'customers': sqlhandler.fill_customers,
        'rentals': sqlhandler.fill_rentals,
    }
    objects = readers[(entity, kind)](path, file_name) if file_name else readers[(entity, kind)](path)
    try:
        sqlhandler.clear_table(entity)
        if objects:
            fillers[entity](objects)
        else:
            sqlhandler.connection.commit()
    except Exception as e:
        sqlhandler.connection.rollback()
        return {'status': 'error', 'message': str(e)}
    names = {'suits': 'Öltönyök', 'customers': 'Ügyfelek', 'rentals': 'Kölcsönzések'}
    return {'status': 'success', 'message': f'{names[entity]} cserélve, {len(objects)} sor'}

def _next_id(table):
    max_id = sqlhandler.get_max_id(table)
    if max_id is None:
        max_id = -1
    return max_id + 1


def add_suit(brand, style, size, color, cost_category_id):
    if not all([brand, style, size, color, cost_category_id]):
        return {'status': 'error', 'message': 'Töltsd ki az öltöny minden mezőjét!'}

    size = int(size)
    cost_category_id = int(cost_category_id)

    if not sqlhandler.does_id_exist_in_table('costcategories', cost_category_id):
        return {'status': 'error', 'message': 'Nincs ilyen árkategória!'}

    suit = Suit(
        id=_next_id('suits'),
        brand=brand,
        style=style,
        size=size,
        color=color,
        cost_category_id=cost_category_id,
    )
    sqlhandler.add_suit(suit)
    return {'status': 'success', 'message': f'Öltöny felvéve, id: {suit.id}'}


def add_customer(first_name, last_name, date_of_birth, is_male, phone):
    if not all([first_name, last_name, date_of_birth, is_male is not None, phone]):
        return {'status': 'error', 'message': 'Töltsd ki az ügyfél minden mezőjét!'}

    date_of_birth = datetime.datetime.strptime(date_of_birth, '%Y.%m.%d')
    is_male_text = str(is_male).strip().lower()
    if is_male_text in ('1', 'true', 'male', 'm', 'ferfi', 'férfi'):
        is_male = 1
    elif is_male_text in ('0', 'false', 'female', 'f', 'no', 'nő'):
        is_male = 0
    else:
        return {'status': 'error', 'message': 'A nem férfi vagy nő legyen!'}

    customer = Customer(
        id=_next_id('customers'),
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        is_male=is_male,
        phone=phone,
    )
    sqlhandler.add_customer(customer)
    return {'status': 'success', 'message': f'Ügyfél felvéve, id: {customer.id}'}


def add_rental(suit_id, customer_id, rental_start, rental_end):
    suit_id = int(suit_id)
    customer_id = int(customer_id)
    rental_start = datetime.datetime.strptime(rental_start, '%Y.%m.%d')
    rental_end = datetime.datetime.strptime(rental_end, '%Y.%m.%d')

    if not sqlhandler.does_id_exist_in_table('suits', suit_id):
        return {'status': 'error', 'message': 'Nincs ilyen öltöny!'}

    if not sqlhandler.does_id_exist_in_table('customers', customer_id):
        return {'status': 'error', 'message': 'Nincs ilyen ügyfél!'}

    if sqlhandler.is_suit_rented(suit_id):
        return {'status': 'error', 'message': 'Ez az öltöny már ki van adva!'}

    max_id = sqlhandler.get_max_id('rentals')
    if max_id is None:
        max_id = -1

    rental = Rental(
        id=max_id + 1,
        suit_id=suit_id,
        customer_id=customer_id,
        rental_start=rental_start,
        rental_end=rental_end
    )

    sqlhandler.add_rental(rental)

    return {'status': 'success', 'message': f'Kölcsönzés kész. Öltöny: {suit_id}, ügyfél: {customer_id}'}


def format_amount(amount):
    amount = str(amount)
    new_amount = ''
    i = 1
    for char in amount[::-1]:
        new_amount += char
        if i % 3 == 0 and i != len(amount):
            new_amount += ','
        i += 1

    return new_amount[::-1] + ' Ft'


def end_rental(rental_id, damage_fee):
    rental_id = int(rental_id)
    damage_fee = int(damage_fee)

    if not sqlhandler.does_id_exist_in_table('rentals', rental_id):
        return {'status': 'error', 'message': 'Nincs ilyen kölcsönzés!'}

    rental = parse_data(sqlhandler.get_row_by_id('rentals', rental_id), Rental)[0]
    suit = parse_data(sqlhandler.get_row_by_id('suits', rental.suit_id), Suit)[0]
    customer = parse_data(sqlhandler.get_row_by_id('customers', rental.customer_id), Customer)[0]
    costcategory = parse_data(sqlhandler.get_row_by_id('costcategories', suit.cost_category_id), CostCategory)[0]

    sqlhandler.remove_row_by_id('rentals', rental_id)

    days_late = max(0, (datetime.datetime.now() - rental.rental_end).days)

    days_between = (rental.rental_end - rental.rental_start).days

    total = int(
        costcategory.price_per_day * days_between
        + costcategory.cleaning_fee
        + damage_fee
        + days_late * costcategory.penalty_per_day_late
    )

    message = (
        f'Öltöny ({suit.id}) visszaérkezett, ügyfél: {customer.id}.\n'
        f'Napok: {days_between} × {format_amount(costcategory.price_per_day)}\n'
        f'Tisztítás: {format_amount(costcategory.cleaning_fee)}\n'
        f'Kár: {format_amount(damage_fee)}\n'
        f'Késés: {days_late} nap × {format_amount(costcategory.penalty_per_day_late)}\n'
        f'Összesen: {format_amount(total)}'
    )

    return {'status': 'success', 'message': message}

def update_cost_category(id, name, price_per_day, cleaning_fee, penalty_per_day):
    id = int(id)
    price_per_day = int(price_per_day) if price_per_day else None
    cleaning_fee = int(cleaning_fee) if cleaning_fee else None
    penalty_per_day = int(penalty_per_day) if penalty_per_day else None

    assert 0 <= id <= 3

    fields = []
    vals = []
    if name:
        fields.append('name')
        vals.append(name)

    if price_per_day:
        fields.append('price_per_day')
        vals.append(price_per_day)

    if cleaning_fee:
        fields.append('cleaning_fee')
        vals.append(cleaning_fee)

    if penalty_per_day:
        fields.append('penalty_per_day_late')
        vals.append(penalty_per_day)

    sqlhandler.update_row('costcategories', id, fields, vals)

    return {'status': 'success', 'message': 'Árkategória mentve'}


sqlhandler = SqlHandler()
sqlhandler.ensure_tables()
