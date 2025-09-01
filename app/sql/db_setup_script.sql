-- ================================================== --
-- First step: granting privileges so app can freely querry in DB
-- ================================================== --

CREATE DATABASE IF NOT EXISTS `cars`
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
USE `cars`;

CREATE USER IF NOT EXISTS 'car_db_user'@'%' IDENTIFIED BY 'car_db_pass';
GRANT ALL PRIVILEGES ON `cars`.* TO 'car_db_user'@'%';
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
    dollar_price SMALLINT NOT NULL CHECK (dollar_price BETWEEN 1000 AND 100000000) -- up to here are the test required response attributes (not null)
    is_new BOOL,
    is_automatic BOOL,
    has_air_conditioning BOOL,
    has_charger_plug BOOL,
    is_armored BOOL,
    has_bt_radio BOOL
);
