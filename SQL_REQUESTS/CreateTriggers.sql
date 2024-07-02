-- Триггер для обеспечения того, чтобы в диете травоядных животных была только растительная пища
CREATE OR REPLACE FUNCTION check_herbivore_diet()
RETURNS TRIGGER AS $$
BEGIN
    IF (NEW.animal_id IS NOT NULL) THEN
        DECLARE
            food_type VARCHAR(50);
            diet_type CHAR(1);
        BEGIN
            SELECT type INTO food_type FROM foods WHERE id = NEW.food_id;
            SELECT predator_or_herbivore INTO diet_type FROM animal WHERE id = NEW.animal_id;

            IF diet_type = 'H' AND food_type != 'Vegetable' THEN
                RAISE EXCEPTION 'Herbivores can only eat vegetable food';
            END IF;
        END;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_herbivore_diet
BEFORE INSERT OR UPDATE ON ration
FOR EACH ROW EXECUTE FUNCTION check_herbivore_diet();

-- Триггер для добавления записи в таблицу enclosureAccess только для работников с доступом к клеткам
CREATE OR REPLACE FUNCTION check_employee_access()
RETURNS TRIGGER AS $$
BEGIN
    IF (NEW.employee_id IS NOT NULL) THEN
        DECLARE
            has_access BOOLEAN;
        BEGIN
            SELECT has_access_to_enclosures INTO has_access FROM employee WHERE id = NEW.employee_id;

            IF has_access = FALSE THEN
                RAISE EXCEPTION 'Employee does not have access to enclosures';
            END IF;
        END;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_employee_access
BEFORE INSERT OR UPDATE ON enclosureAccess
FOR EACH ROW EXECUTE FUNCTION check_employee_access();

-- Триггер для автоматического заполнения поля has_access_to_enclosures в таблице employee в зависимости от должности
CREATE OR REPLACE FUNCTION set_access_to_enclosures()
RETURNS TRIGGER AS $$
BEGIN
    IF (NEW.position IS NOT NULL) THEN
        IF NEW.position IN ('Veterinarian', 'Trainer', 'Cleaner') THEN
            NEW.has_access_to_enclosures := TRUE;
        ELSE
            NEW.has_access_to_enclosures := FALSE;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_set_access_to_enclosures
BEFORE INSERT OR UPDATE ON employee
FOR EACH ROW EXECUTE FUNCTION set_access_to_enclosures();

-- Триггер, чтобы только ветеренары могли оставлять записи в мед.карте.
CREATE OR REPLACE FUNCTION is_veterinarian(employee_id INT) RETURNS BOOLEAN AS $$
DECLARE
    pos VARCHAR(50);
BEGIN
    SELECT position INTO pos FROM employee WHERE id = employee_id;
    RETURN pos = 'Veterinarian';
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION check_veterinarian_permission() RETURNS TRIGGER AS $$
BEGIN
    IF NOT is_veterinarian(NEW.employee_id) THEN
        RAISE EXCEPTION 'Only veterinarians can add information to vetCard table';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER vetcard_permission_trigger
BEFORE INSERT OR UPDATE ON vetCard
FOR EACH ROW
EXECUTE FUNCTION check_veterinarian_permission();