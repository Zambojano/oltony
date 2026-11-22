import datetime
from dataclasses import dataclass, field

@dataclass
class Suit:
    id: int = field()
    brand: str = field()
    style: str = field()
    size: int = field()
    color: str = field()
    cost_category_id: int = field()

@dataclass
class Customer:
    id: int = field()
    first_name: str = field()
    last_name: str = field()
    date_of_birth: datetime.datetime = field()
    is_male: int = field()
    phone: str = field()

@dataclass
class Rental:
    id: int = field()
    suit_id: int = field()
    customer_id: int = field()
    rental_start: datetime.datetime = field()
    rental_end: datetime.datetime = field()

@dataclass
class CostCategory:
    id: int
    name: str
    price_per_day: float
    cleaning_fee: float
    penalty_per_day_late: float


def parse_data(datas, Obj):
    result = []
    for data in datas:
        result.append(
            Obj(
                *data
            )
        )
    return result
