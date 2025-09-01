import random
from dao import DAOCar
from db_utils import DBConn
from makers_and_models import MAKERS_AND_MODELS
from datetime import date


COLORS = ["black","white","silver","gray","red","blue","green","yellow","orange","brown"]
FUEL_ENUM = ['gasoline','flex','diesel','electric','hybrid']


class DBSeeder:

    def __init__(self, seed_count: int=100):
        self.seed_count = seed_count

    def run(self):
        self.create_db_conn()
        self.add_random_data()
        try:
            self.db_conn.commit()
        except:
            print('failed seed script. debug and try again')
        finally:
            self.db_conn.close()

    def create_db_conn(self):
        self.db_conn = DBConn()
        self.db_conn.connect()

    def add_random_data(self):
        makes = list(MAKERS_AND_MODELS.keys())
        for i in range(self.seed_count):
            make = random.choices(makes)
            year = random.randint(1980,2025)
            dao = DAOCar()
            dao.make = make
            dao.model = random.choice(MAKERS_AND_MODELS[make])
            dao.year = random.randint(1980, 2025)
            dao.color = random.choice(COLORS)
            dao.fuel = random.choice(FUEL_ENUM)
            dao.mileage = self.mileage_considering_year()
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
        min_mileage = 12000 * car_age # in miles, estimate found with google search
        max_mileage = 15000 * car_age
       
        return random.randint(min_mileage, max_mileage)



if __name__ == "__main__":
    DBSeeder(seed_count=100).run()
