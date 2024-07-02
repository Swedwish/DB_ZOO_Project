-- Отключить временно проверку внешних ключей
SET session_replication_role = replica;

-- Удаление всех таблиц
DROP TABLE IF EXISTS employeeAttributes;
DROP TABLE IF EXISTS enclosureAccess;
DROP TABLE IF EXISTS animalsInEnclosure;
DROP TABLE IF EXISTS ration;
DROP TABLE IF EXISTS supplies;
DROP TABLE IF EXISTS vetCard CASCADE;
DROP TABLE IF EXISTS animalCompatability;
DROP TABLE IF EXISTS foods;
DROP TABLE IF EXISTS animal;
DROP TABLE IF EXISTS enclosure;
DROP TABLE IF EXISTS employee;

-- Включить проверку внешних ключей обратно
SET session_replication_role = origin;