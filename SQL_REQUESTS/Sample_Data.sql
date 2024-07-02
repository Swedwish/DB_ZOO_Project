-- Вставка данных в таблицу employee
INSERT INTO employee (name, position, sex, age, start_date, has_access_to_enclosures, salary)
VALUES 
('John Doe', 'Veterinarian', 'M', 35, '2020-01-15', TRUE, 50000.00),
('Jane Smith', 'Trainer', 'F', 28, '2018-03-22', TRUE, 45000.00),
('Michael Brown', 'Cleaner', 'M', 45, '2015-06-30', TRUE, 30000.00),
('Emily White', 'Administrator', 'F', 32, '2019-09-10', FALSE, 40000.00);

-- Вставка данных в таблицу employeeAttributes
INSERT INTO employeeAttributes (employee_id, attribute_name, attribute_value)
VALUES 
(1, 'Specialization', 'Large Animals'),
(2, 'Specialization', 'Primates'),
(3, 'Shift', 'Night'),
(4, 'AccessLevel', 'High');

-- Вставка данных в таблицу enclosure
INSERT INTO enclosure (size, is_heated)
VALUES 
(100, TRUE),
(200, FALSE),
(150, TRUE);

-- Вставка данных в таблицу enclosureAccess
INSERT INTO enclosureAccess (enclosure_id, employee_id)
VALUES 
(1, 1),
(2, 2),
(3, 3);

-- Вставка данных в таблицу foods
INSERT INTO foods (type, name)
VALUES 
('Vegetable', 'Carrot'),
('Meat', 'Chicken'),
('Vegetable', 'Banana');

-- Вставка данных в таблицу supplies
INSERT INTO supplies (food_id, supplier_name)
VALUES 
(1, 'Farm Supplier A'),
(2, 'Butcher B'),
(3, 'Fruit Vendor C');

-- Вставка данных в таблицу animal
INSERT INTO animal (species, needs_heated_enclosure_for_winter, predator_or_herbivore, gender, date_of_birth, arrival_date, father_id, mother_id)
VALUES 
('Lion', TRUE, 'P', 'M', '2015-05-10', '2015-06-01', NULL, NULL),
('Giraffe', FALSE, 'H', 'F', '2016-07-21', '2016-08-15', NULL, NULL),
('Monkey', FALSE, 'H', 'M', '2018-11-30', '2019-01-10', NULL, NULL);

-- Вставка данных в таблицу animalsInEnclosure
INSERT INTO animalsInEnclosure (enclosure_id, animal_id)
VALUES 
(1, 1),
(2, 2),
(3, 3);

-- Вставка данных в таблицу vetCard
INSERT INTO vetCard (employee_id, animal_id, current_diseases, got_vaccination, date, weight, height)
VALUES 
(1, 1, 'Healthy', TRUE, '2023-01-01', 190.5, 1.2),
(1, 2, 'Minor Injury', TRUE, '2023-01-05', 800.0, 5.5),
(2, 3, 'Healthy', TRUE, '2023-01-10', 30.2, 0.9);

-- Вставка данных в таблицу ration
INSERT INTO ration (day_of_the_week, time, food_id, animal_id)
VALUES 
('Monday', '08:00:00', 1, 1),
('Tuesday', '12:00:00', 2, 2),
('Wednesday', '18:00:00', 3, 3);

-- Вставка данных в таблицу animalCompatability
INSERT INTO animalCompatability (first_species, second_species, is_compatible)
VALUES 
('Lion', 'Giraffe', FALSE),
('Monkey', 'Giraffe', TRUE);