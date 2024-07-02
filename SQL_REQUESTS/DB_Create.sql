-- Таблица для хранения работников
CREATE TABLE employee (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    position VARCHAR(50),
    sex CHAR(1),
    age INT,
    start_date DATE,
    has_access_to_enclosures BOOLEAN,
    salary DECIMAL(10, 2)
);

-- Таблица для хранения атрибутов работников
CREATE TABLE employeeAttributes (
    id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES employee(id),
    attribute_name VARCHAR(50),
    attribute_value VARCHAR(100)
);

-- Таблица для хранения клеток
CREATE TABLE enclosure (
    id SERIAL PRIMARY KEY,
    size INT,
    is_heated BOOLEAN
);

-- Таблица для хранения доступа работников к клеткам
CREATE TABLE enclosureAccess (
    enclosure_id INT REFERENCES enclosure(id),
    employee_id INT REFERENCES employee(id),
    PRIMARY KEY (enclosure_id, employee_id)
);

-- Таблица для хранения кормов
CREATE TABLE foods (
    id SERIAL PRIMARY KEY,
    type VARCHAR(50),
    name VARCHAR(50)
);

-- Таблица для хранения поставщиков кормов
CREATE TABLE supplies (
    id SERIAL PRIMARY KEY,
    food_id INT REFERENCES foods(id),
    supplier_name VARCHAR(50)
);

-- Таблица для хранения животных
CREATE TABLE animal (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50),
    species VARCHAR(50),
    needs_heated_enclosure_for_winter BOOLEAN,
    predator_or_herbivore CHAR(1),
    gender CHAR(1),
    date_of_birth DATE,
    arrival_date DATE,
    father_id INT REFERENCES animal(id),
    mother_id INT REFERENCES animal(id),
    enclosure_id INT REFERENCES enclosure(id)
);


-- Таблица для хранения ветеринарных карт
CREATE TABLE vetCard (
    id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES employee(id),
    animal_id INT REFERENCES animal(id),
    current_diseases VARCHAR(100),
    got_vaccination VARCHAR(100),
    date DATE,
    weight DECIMAL(5, 2),
    height DECIMAL(5, 2)
);

-- Таблица для хранения рациона животных
CREATE TABLE ration (
    id SERIAL PRIMARY KEY,
    day_of_the_week VARCHAR(10),
    time TIME,
    food_id INT REFERENCES foods(id),
    animal_id INT REFERENCES animal(id)
);

-- Таблица для хранения совместимости животных
CREATE TABLE animalCompatibility (
    id SERIAL PRIMARY KEY,
    first_species VARCHAR(50),
    second_species VARCHAR(50),
    is_compatible BOOLEAN
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE
);

-- Таблица employee
ALTER TABLE employee
ADD CONSTRAINT position_check
CHECK (position IN ('Veterinarian', 'Cleaner', 'Trainer', 'Builder', 'Administrator'));

-- Таблица foods
ALTER TABLE foods
ADD CONSTRAINT type_check
CHECK (type IN ('Vegetable', 'Live', 'Meat', 'Mixed'));

-- Таблица animal
ALTER TABLE animal
ADD CONSTRAINT predator_or_herbivore_check
CHECK (predator_or_herbivore IN ('P', 'H'));

ALTER TABLE animal
ADD enclosure_id INT REFERENCES enclosure(id);