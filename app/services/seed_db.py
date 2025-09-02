import random
import time
import traceback
from app.dao.car_market import DAOCar
from app.db_utils.db_connection import DBConn
from app.services.makers_and_models import MAKERS_AND_MODELS
from datetime import date


COLORS = ["black","white","silver","gray","red","blue","green","yellow","orange","brown"]
FUEL_ENUM = ['gasoline','flex','diesel','electric','hybrid']


class DBSeeder:

    def __init__(self, seed_count: int=100):
        self.seed_count = seed_count

    def run(self):
        time.sleep(12)
        for i in range(6): # had too many issues in auto-start seeder
            try:
                self.create_db_conn()
                self.add_random_data()
                self.db_conn.commit()
                time.sleep(2)
                break
            except Exception as e:
                print(f'failed seed script. debug and try again. {e}')
                traceback.print_exc()
            finally:
                self.db_conn.disconnect()

    def create_db_conn(self):
        self.db_conn = DBConn()
        self.db_conn.connect()

    def add_random_data(self):
        makes = list(MAKERS_AND_MODELS.keys())
        for i in range(self.seed_count):
            make = random.choice(makes)
            year = random.randint(1980,2025)
            dao = DAOCar()
            dao.make = make
            dao.model = random.choice(MAKERS_AND_MODELS[make])
            dao.year = year
            dao.color = random.choice(COLORS)
            dao.fuel = random.choice(FUEL_ENUM)
            dao.mileage = self.mileage_considering_year(year)
            # Keeping random for test purposes. For more realistic prices, a function considering attributes could be applied 
            dao.dollar_price = random.randint(4000, 120000)
            dao.is_new = random.choice([True, False])
            dao.is_automatic = random.choice([True, False])
            dao.has_air_conditioning = random.choice([True, False])
            dao.has_charger_plug = random.choice([True, False])
            dao.is_armored = random.choice([True, False])
            dao.has_bt_radio = random.choice([True, False])
            
            self.db_conn.add(dao)

    @staticmethod
    def mileage_considering_year(car_fabrication_year:int) -> int:
        current_year = date.today().year
        car_age = current_year - car_fabrication_year
        car_age = max(0, car_age) # car age never below zero
        min_mileage = 12000 * car_age # in miles, estimate found with google search
        max_mileage = 15000 * car_age
       
        return random.randint(min_mileage, max_mileage)



if __name__ == "__main__":
    DBSeeder(seed_count=100).run()
