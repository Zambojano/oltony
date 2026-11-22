from faker import Faker
from models import Suit, Customer, CostCategory
import random
from datetime import datetime, timedelta


BRANDS = [
    'Hugo Boss', 'Calvin Klein', 'Zara', 'Massimo Dutti', 'Tommy Hilfiger',
    'Armani', 'Digel', 'Carl Gross', 'Pierre Cardin', 'Selected',
]
STYLES = ['slim', 'klasszikus', 'smoking', 'háromrészes', 'kétsoros']
SIZES = [44, 46, 48, 50, 52, 54, 56, 58, 60]
COLORS = ['fekete', 'sötétkék', 'szürke', 'antracit', 'bordó', 'bézs']


def generate_suits(n: int, category_distribution):
    if n is None:
        n = 1000
    if category_distribution is None:
        category_distribution = [50, 10, 5, 35]

    assert n >= 0
    assert sum(category_distribution) == 100

    suits = []

    for i in range(n):
        num = int(random.random() * 100)
        s = 0
        cost_category_id = None
        for k, val in enumerate(category_distribution):
            s += val
            if num <= s:
                cost_category_id = k
                break

        suits.append(Suit(
            id=i,
            brand=random.choice(BRANDS),
            style=random.choice(STYLES),
            size=random.choice(SIZES),
            color=random.choice(COLORS),
            cost_category_id=cost_category_id
        ))

    return suits


def generate_customers(n: int, male_ratio: float, customers_locale: str):
    n = n if n else 1000
    male_ratio = male_ratio if male_ratio else 0.5
    customers_locale = customers_locale if customers_locale else 'hu_HU'

    assert n >= 0
    assert 0 <= male_ratio <= 1

    fake = Faker(customers_locale)
    customers = []

    for i in range(n):
        start_date = datetime.strptime('1950.01.01', '%Y.%m.%d')
        end_date = datetime.strptime('2025.12.31', '%Y.%m.%d')

        is_male = 1 if random.random() < male_ratio else 0
        phone = '06' + ''.join(random.choice('0123456789') for _ in range(9))

        customers.append(
            Customer(
                id = i,
                first_name = fake.first_name_male() if is_male else fake.first_name_female(),
                last_name = fake.last_name(),
                date_of_birth = start_date + timedelta(days=random.randrange((end_date - start_date).days)),
                is_male = is_male,
                phone = phone
            )
        )

    return customers

def generate_costcategories():
    categories = []
    categories.append(
        CostCategory(
            id=0,
            name='olcso',
            price_per_day=5_000,
            cleaning_fee=2_500,
            penalty_per_day_late=4_000
        )
    )
    categories.append(
        CostCategory(
            id=1,
            name='alap',
            price_per_day=9_000,
            cleaning_fee=3_500,
            penalty_per_day_late=7_000
        )
    )
    categories.append(
        CostCategory(
            id=2,
            name='draga',
            price_per_day=16_000,
            cleaning_fee=5_000,
            penalty_per_day_late=12_000
        )
    )
    categories.append(
        CostCategory(
            id=3,
            name='luxus',
            price_per_day=28_000,
            cleaning_fee=8_000,
            penalty_per_day_late=20_000
        )
    )
    return categories
