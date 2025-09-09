-- ================================================== --
-- First step: granting privileges so app can freely querry in DB
-- ================================================== --

CREATE DATABASE IF NOT EXISTS `cars`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE `cars`;

CREATE USER IF NOT EXISTS 'car_user'@'%' IDENTIFIED WITH mysql_native_password BY 'car_pass';
GRANT ALL PRIVILEGES ON `cars`.* TO 'car_user'@'%';
FLUSH PRIVILEGES; 

-- ================================================== --
-- tables
-- ================================================== --

CREATE TABLE car_market  (
    id INT AUTO_INCREMENT PRIMARY KEY,
    make VARCHAR(25) NOT NULL,
    model VARCHAR(45) NOT NULL,
    year SMALLINT UNSIGNED NOT NULL CHECK (year BETWEEN 1900 AND 2100),
    color VARCHAR(25) NOT NULL,
    fuel ENUM('gasoline','flex','diesel','electric','hybrid') NOT NULL,
    mileage INT UNSIGNED NOT NULL,
    dollar_price INT NOT NULL CHECK (dollar_price BETWEEN 1000 AND 100000000), -- up to here are the test required response attributes (not null)
    is_new BOOL,
    is_automatic BOOL,
    has_air_conditioning BOOL,
    has_charger_plug BOOL,
    is_armored BOOL,
    has_bt_radio BOOL
);

-- ================================================== --
-- seed for test
-- ================================================== --
INSERT INTO car_market
(make, model, year, color, fuel, mileage, dollar_price, is_new, is_automatic, has_air_conditioning, has_charger_plug, is_armored, has_bt_radio)
VALUES
('Honda','Civic',2024,'white','flex',1200,32000,TRUE,TRUE,TRUE,FALSE,FALSE,TRUE),

('Honda','HR-V',2022,'black','gasoline',22000,24000,FALSE,TRUE,TRUE,FALSE,FALSE,TRUE),
('Honda','Civic',2018,'silver','flex',65000,16000,FALSE,TRUE,TRUE,FALSE,FALSE,TRUE),

('Tesla','Model 3',2019,'red','electric',85000,30000,FALSE,TRUE,TRUE,TRUE,FALSE,TRUE),
('Nissan','Leaf',2017,'green','electric',92000,14000,FALSE,TRUE,TRUE,TRUE,FALSE,TRUE),

('Toyota','Corolla',2019,'gray','flex',80000,17000,FALSE,TRUE,TRUE,FALSE,FALSE,TRUE),
('Jeep','Compass',2019,'white','flex',80000,20000,FALSE,TRUE,TRUE,FALSE,FALSE,TRUE),

('Toyota','Hilux',2020,'brown','diesel',70000,38000,FALSE,TRUE,TRUE,FALSE,FALSE,TRUE),
('Ford','Fiesta',2014,'blue','gasoline',130000,6000,FALSE,FALSE,TRUE,FALSE,FALSE,TRUE),
('Chevrolet','Onix',2021,'black','flex',30000,12000,FALSE,FALSE,TRUE,FALSE,FALSE,TRUE),
('Volkswagen','Golf',2016,'white','gasoline',90000,10000,FALSE,FALSE,TRUE,FALSE,FALSE,TRUE);
