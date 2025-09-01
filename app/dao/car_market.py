import sqlalchemy
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DAOCar(Base):
    __tablename__ = "car_market"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    make = sqlalchemy.Column(sqlalchemy.String(25), nullable=False)
    model = sqlalchemy.Column(sqlalchemy.String(45), nullable=False)
    year = sqlalchemy.Column(sqlalchemy.SmallInteger, nullable=False)
    color = sqlalchemy.Column(sqlalchemy.String(25), nullable=False)
    fuel = sqlalchemy.Column(sqlalchemy.Enum("gasoline", "flex", "diesel", "electric", "hybrid", name="fuel_enum"), nullable=False)
    mileage = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    dollar_price = sqlalchemy.Column(sqlalchemy.Numeric(9, 2), nullable=False)
    is_automatic = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    has_air_conditioning = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    has_charger_plug = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    is_armored = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    has_bt_radio = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
