
import oracledb
from models import Suit, Customer, Rental, CostCategory
import pwinput

class SqlHandler:
    def __init__(self):
        pw = pwinput.pwinput(prompt="Enter password: ", mask="#")

        self.connection = oracledb.connect(
            user="U_EV7MAJ",
            password=pw,
            dsn="codd.inf.unideb.hu:1521/ora21cp.inf.unideb.hu")

        self.cursor = self.connection.cursor()

        self.table_names = {
            'suits': 'suits',
            'customers': 'suit_customers',
            'rentals': 'suit_rentals',
            'costcategories': 'suit_categories',
        }

    def _table(self, name: str) -> str:
        if name not in self.table_names:
            raise ValueError(f'Unknown table: {name}')
        return self.table_names[name]

    def ensure_tables(self):
        try:
            self.cursor.execute("""
            create table suits (
                id number primary key,
                brand varchar2(30),
                style varchar2(30),
                suit_size number,
                color varchar2(20),
                cost_category_id number
            )
            """)
            print('Suits table created!')
        except oracledb.DatabaseError as e:
            print('Suits table already exists!')

        try:
            self.cursor.execute("""
                create table suit_customers (
                    id number primary key,
                    first_name varchar2(30),
                    last_name varchar2(30),
                    date_of_birth date,
                    is_male number(1),
                    phone varchar2(20))
            """)
            print('Customers table created!')
        except oracledb.DatabaseError as e:
            print('Customers table already exists!')
            try:
                self.cursor.execute('alter table suit_customers add phone varchar2(20)')
            except oracledb.DatabaseError:
                pass

        try:
            self.cursor.execute("""
                create table suit_rentals (
                    id number primary key,
                    suit_id number,
                    customer_id number,
                    rental_start date,
                    rental_end date)
            """)
            print('Rentals table created!')
        except oracledb.DatabaseError as e:
            print('Rentals table already exists!')

        try:
            self.cursor.execute("""
                create table suit_categories (
                    id number primary key,
                    name varchar2(20),
                    price_per_day number,
                    cleaning_fee number,
                    penalty_per_day_late number)
            """)
            print('Costcategories table created!')
        except oracledb.DatabaseError as e:
            print('Costcategories table already exists!')

        self.connection.commit()

    def drop_all(self):
        for table in self.table_names.values():
            try:
                self.cursor.execute(f"""
                    drop table {table}
                """)
                print(table, 'dropped')
            except Exception as e:
                print(table, 'does not exist')

        self.connection.commit()

    def add_suit(self, suit: Suit):
        self.cursor.execute('''
            insert into suits (id, brand, style, suit_size, color, cost_category_id) values (:id, :brand, :style, :suit_size, :color, :cost_category_id)
        ''', id=suit.id, brand=suit.brand, style=suit.style, suit_size=suit.size, color=suit.color, cost_category_id=suit.cost_category_id)

        self.connection.commit()

    def add_customer(self, customer: Customer):
        self.cursor.execute('''
            insert into suit_customers (id, first_name, last_name, date_of_birth, is_male, phone) values (:id, :first_name, :last_name, :date_of_birth, :is_male, :phone)
        ''', id=customer.id, first_name=customer.first_name, last_name=customer.last_name, date_of_birth=customer.date_of_birth, is_male=customer.is_male, phone=customer.phone)

        self.connection.commit()

    def add_rental(self, rental: Rental):
        self.cursor.execute('''
            insert into suit_rentals (id, suit_id, customer_id, rental_start, rental_end) values (:id, :suit_id, :customer_id, :rental_start, :rental_end)
        ''', id=rental.id, suit_id=rental.suit_id, customer_id=rental.customer_id, rental_start=rental.rental_start, rental_end=rental.rental_end)

        self.connection.commit()

    def add_costcategory(self, costcategory: CostCategory):
        self.cursor.execute('''
            insert into suit_categories (id, name, price_per_day, cleaning_fee, penalty_per_day_late) values (:id, :name, :price_per_day, :cleaning_fee, :penalty_per_day_late)
        ''', id=costcategory.id, name=costcategory.name, price_per_day=costcategory.price_per_day, cleaning_fee=costcategory.cleaning_fee, penalty_per_day_late=costcategory.penalty_per_day_late)

        self.connection.commit()

    def fill_suits(self, suits):
        self.cursor.executemany("insert into suits (id, brand, style, suit_size, color, cost_category_id) values(:id, :brand, :style, :suit_size, :color, :cost_category_id)",
                                [[suit.id, suit.brand, suit.style, suit.size, suit.color, suit.cost_category_id] for suit in suits])
        self.connection.commit()

    def fill_customers(self, customers):
        self.cursor.executemany("insert into suit_customers (id, first_name, last_name, date_of_birth, is_male, phone) values (:id, :first_name, :last_name, :date_of_birth, :is_male, :phone)",
                                [[customer.id, customer.first_name, customer.last_name, customer.date_of_birth, customer.is_male, customer.phone] for customer in customers])
        self.connection.commit()

    def fill_costcategories(self, categories):
        self.cursor.executemany("insert into suit_categories (id, name, price_per_day, cleaning_fee, penalty_per_day_late) values (:id, :name, :price_per_day, :cleaning_fee, :penalty_per_day_late)",
                                [[category.id, category.name, category.price_per_day, category.cleaning_fee, category.penalty_per_day_late] for category in categories])
        self.connection.commit()

    def fill_rentals(self, rentals):
        self.cursor.executemany(
            "insert into suit_rentals (id, suit_id, customer_id, rental_start, rental_end) values (:id, :suit_id, :customer_id, :rental_start, :rental_end)",
            [[rental.id, rental.suit_id, rental.customer_id, rental.rental_start, rental.rental_end] for rental in rentals]
        )
        self.connection.commit()

    def clear_table(self, table: str):
        self.cursor.execute(f'delete from {self._table(table)}')

    def read_table(self, table: str):
        self.cursor.execute(f'''
            select * from {self._table(table)} order by id
        ''')
        return self.cursor.fetchall()

    def get_max_id(self, table: str):
        self.cursor.execute(f'''
            select max(id) from {self._table(table)}
        ''')
        return self.cursor.fetchall()[0][0]

    def is_suit_rented(self, suit_id: int):
        self.cursor.execute(f'''
            select * from suit_rentals where suit_id = {suit_id}
        ''')
        return len(self.cursor.fetchall()) != 0

    def does_id_exist_in_table(self, table: str, id: int):
        self.cursor.execute(f'''
            select * from {self._table(table)} where id = {id}
        ''')
        return len(self.cursor.fetchall()) != 0

    def get_row_by_id(self, table: str, id: int):
        self.cursor.execute(f'''
            select * from {self._table(table)} where id = {id}
        ''')
        return self.cursor.fetchall()

    def remove_row_by_id(self, table: str, id: int):
        self.cursor.execute(f'''
            delete from {self._table(table)} where id = {id}
        ''')
        self.connection.commit()

    def update_row(self, table: str, id: int, fields: list[str], new_vals: list):
        set = ''
        i = 0
        for field, val in zip(fields, new_vals):
            if isinstance(field, str):
                set = set + f"{field} = '{val}'" + (',' if i != len(fields) - 1 else '')
            elif isinstance(field, int):
                set = set + f'{field} = {val}' + (',' if i != len(fields) - 1 else '')
            i += 1
        physical = self._table(table)
        print(f'update {physical} set {set} where id = {id}')
        self.cursor.execute(f'''
            update {physical} set {set} where id = {id}
        ''')
        self.connection.commit()
