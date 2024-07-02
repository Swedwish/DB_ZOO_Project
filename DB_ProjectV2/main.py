from datetime import date, datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Query, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sqlalchemy import DECIMAL, Date, ForeignKey, Time, and_, create_engine, Column, Integer, String, Boolean, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, aliased
from sqlalchemy.orm import relationship
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt

# ------------------------------------------- INITIALISATION -----------------------------------------
# Database configuration
DATABASE_URL = "postgresql://postgres:0000@localhost/Zoo DB" 
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Create tables
Base = declarative_base()
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------------------------- EMPLOYEES -----------------------------------------
# Employee model
class Employee(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    position = Column(String)
    sex = Column(String)
    age = Column(Integer)
    start_date = Column(String)
    has_access_to_enclosures = Column(Boolean)
    salary = Column(Integer)
    
    attributes = relationship("EmployeeAttribute", back_populates="employee")
    access = relationship("EnclosureAccess", back_populates="employee")
      
# Pydantic schemas
class EmployeeCreate(BaseModel):
    name: str
    position: str
    sex: str
    age: int
    start_date: str
    salary: int
    
@app.get("/employees", response_class=HTMLResponse)
def read_employees(request: Request, db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    return templates.TemplateResponse("employees.html", {"request": request, "employees": employees})

@app.post("/employees/create", response_class=HTMLResponse)
def create_employee(
    name: str = Form(...),
    position: str = Form(...),
    sex: str = Form(...),
    age: int = Form(...),
    start_date: str = Form(...),
    salary: int = Form(...),
    db: Session = Depends(get_db)
):
    db_employee = Employee(
        name=name,
        position=position,
        sex=sex,
        age=age,
        start_date=start_date,
        salary=salary,
        has_access_to_enclosures=position in ['Veterinarian', 'Cleaner', 'Trainer']
    )
    db.add(db_employee)
    db.commit()
    return RedirectResponse(url="/employees", status_code=303)

@app.post("/employees/edit/{employee_id}", response_class=HTMLResponse)
def edit_employee(
    employee_id: int,
    name: str = Form(...),
    position: str = Form(...),
    sex: str = Form(...),
    age: int = Form(...),
    start_date: str = Form(...),
    salary: int = Form(...),
    db: Session = Depends(get_db)
):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    db_employee.name = name
    db_employee.position = position
    db_employee.sex = sex
    db_employee.age = age
    db_employee.start_date = start_date
    db_employee.salary = salary
    db_employee.has_access_to_enclosures = position in ['Veterinarian', 'Cleaner', 'Trainer']

    db.commit()
    return RedirectResponse(url="/employees", status_code=303)

@app.post("/employees/delete/{employee_id}", response_class=HTMLResponse)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(db_employee)
    db.commit()
    return RedirectResponse(url="/employees", status_code=303)

# ------------------------------------------- ANIMALS -----------------------------------------
class Animal(Base):
    __tablename__ = 'animal'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    species = Column(String, nullable=False)
    needs_heated_enclosure_for_winter = Column(Boolean, nullable=False)
    predator_or_herbivore = Column(String(1), nullable=False)
    gender = Column(String(1), nullable=False)
    date_of_birth = Column(Date, nullable=False)
    arrival_date = Column(Date, nullable=False)
    father_id = Column(Integer, ForeignKey('animal.id'), nullable=True)
    mother_id = Column(Integer, ForeignKey('animal.id'), nullable=True)
    enclosure_id = Column(Integer, ForeignKey('enclosure.id'), nullable=False)

    father = relationship("Animal", remote_side=[id], foreign_keys=[father_id], backref="fathered")
    mother = relationship("Animal", remote_side=[id], foreign_keys=[mother_id], backref="mothered")
    enclosure = relationship("Enclosure", back_populates="animals")
    

@app.get("/animals", response_class=HTMLResponse)
def read_animals(request: Request, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    animals = db.query(Animal).offset(skip).limit(limit).all()
    return templates.TemplateResponse("animals.html", {"request": request, "animals": animals})

@app.post("/animals/create", response_class=HTMLResponse)
def create_animal(
    request: Request,
    name: str = Form(...),
    species: str = Form(...),
    needs_heated_enclosure_for_winter: bool = Form(...),
    predator_or_herbivore: str = Form(...),
    gender: str = Form(...),
    date_of_birth: str = Form(...),
    arrival_date: str = Form(...),
    father_id: int = Form(None),
    mother_id: int = Form(None),
    enclosure_id: int = Form(...),
    db: Session = Depends(get_db)
):
    animal = Animal(
        name=name,
        species=species,
        needs_heated_enclosure_for_winter=needs_heated_enclosure_for_winter,
        predator_or_herbivore=predator_or_herbivore,
        gender=gender,
        date_of_birth=date_of_birth,
        arrival_date=arrival_date,
        father_id=father_id,
        mother_id=mother_id,
        enclosure_id=enclosure_id
    )
    db.add(animal)
    db.commit()
    db.refresh(animal)
    return RedirectResponse(url="/animals", status_code=303)

@app.post("/animals/edit/{animal_id}", response_class=HTMLResponse)
def edit_animal(
    request: Request,
    animal_id: int,
    name: str = Form(...),
    species: str = Form(...),
    needs_heated_enclosure_for_winter: bool = Form(...) or False,
    predator_or_herbivore: str = Form(...),
    gender: str = Form(...),
    date_of_birth: str = Form(...),
    arrival_date: str = Form(...),
    father_id: int = Form(None),
    mother_id: int = Form(None),
    enclosure_id: int = Form(...),
    db: Session = Depends(get_db)
):
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")

    animal.name = name
    animal.species = species
    animal.needs_heated_enclosure_for_winter = needs_heated_enclosure_for_winter or False
    animal.predator_or_herbivore = predator_or_herbivore
    animal.gender = gender
    animal.date_of_birth = date_of_birth
    animal.arrival_date = arrival_date
    animal.father_id = father_id
    animal.mother_id = mother_id
    animal.enclosure_id = enclosure_id

    db.commit()
    db.refresh(animal)
    return RedirectResponse(url="/animals", status_code=303)

@app.post("/animals/delete/{animal_id}", response_class=HTMLResponse)
def delete_animal(request: Request, animal_id: int, db: Session = Depends(get_db)):
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal not found")

    db.delete(animal)
    db.commit()
    return RedirectResponse(url="/animals", status_code=303)

# ------------------------------------------- EMPLOYEE ATTRIBUTES -----------------------------------------

class EmployeeAttribute(Base):
    __tablename__ = 'employeeattributes'

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employee.id'), nullable=False)
    attribute_name = Column(String, nullable=False)
    attribute_value = Column(String, nullable=False)

    employee = relationship("Employee", back_populates="attributes")
    
@app.get("/employee-attributes", response_class=HTMLResponse)
def read_employee_attributes(request: Request, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    attributes = db.query(EmployeeAttribute).offset(skip).limit(limit).all()
    return templates.TemplateResponse("employee_attributes.html", {"request": request, "attributes": attributes})

@app.post("/employee-attributes/create", response_class=HTMLResponse)
def create_employee_attribute(
    request: Request,
    employee_id: int = Form(...),
    attribute_name: str = Form(...),
    attribute_value: str = Form(...),
    db: Session = Depends(get_db)
):
    attribute = EmployeeAttribute(
        employee_id=employee_id,
        attribute_name=attribute_name,
        attribute_value=attribute_value,
    )
    db.add(attribute)
    db.commit()
    db.refresh(attribute)
    return RedirectResponse(url="/employee-attributes", status_code=303)

@app.post("/employee-attributes/edit/{attribute_id}", response_class=HTMLResponse)
def edit_employee_attribute(
    request: Request,
    attribute_id: int,
    employee_id: int = Form(...),
    attribute_name: str = Form(...),
    attribute_value: str = Form(...),
    db: Session = Depends(get_db)
):
    attribute = db.query(EmployeeAttribute).filter(EmployeeAttribute.id == attribute_id).first()
    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")

    attribute.employee_id = employee_id
    attribute.attribute_name = attribute_name
    attribute.attribute_value = attribute_value

    db.commit()
    db.refresh(attribute)
    return RedirectResponse(url="/employee-attributes", status_code=303)

@app.post("/employee-attributes/delete/{attribute_id}", response_class=HTMLResponse)
def delete_employee_attribute(request: Request, attribute_id: int, db: Session = Depends(get_db)):
    attribute = db.query(EmployeeAttribute).filter(EmployeeAttribute.id == attribute_id).first()
    if not attribute:
        raise HTTPException(status_code=404, detail="Attribute not found")

    db.delete(attribute)
    db.commit()
    return RedirectResponse(url="/employee-attributes", status_code=303)


# ------------------------------------------- ENCLOSURE -----------------------------------------
class Enclosure(Base):
    __tablename__ = 'enclosure'

    id = Column(Integer, primary_key=True, index=True)
    size = Column(Integer, nullable=False)
    is_heated = Column(Boolean, nullable=False)
    
    access = relationship("EnclosureAccess", back_populates="enclosure")
    animals = relationship("Animal", back_populates="enclosure")
    
@app.get("/enclosures", response_class=HTMLResponse)
def read_enclosures(request: Request, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    enclosures = db.query(Enclosure).offset(skip).limit(limit).all()
    return templates.TemplateResponse("enclosures.html", {"request": request, "enclosures": enclosures})

@app.post("/enclosures/create", response_class=HTMLResponse)
def create_enclosure(
    request: Request,
    size: int = Form(...),
    is_heated: bool = Form(...),
    db: Session = Depends(get_db)
):
    enclosure = Enclosure(
        size=size,
        is_heated=is_heated,
    )
    db.add(enclosure)
    db.commit()
    db.refresh(enclosure)
    return RedirectResponse(url="/enclosures", status_code=303)

@app.post("/enclosures/edit/{enclosure_id}", response_class=HTMLResponse)
def edit_enclosure(
    request: Request,
    enclosure_id: int,
    size: int = Form(...),
    is_heated: bool = Form(...),
    db: Session = Depends(get_db)
):
    enclosure = db.query(Enclosure).filter(Enclosure.id == enclosure_id).first()
    if not enclosure:
        raise HTTPException(status_code=404, detail="Enclosure not found")

    enclosure.size = size
    enclosure.is_heated = is_heated

    db.commit()
    db.refresh(enclosure)
    return RedirectResponse(url="/enclosures", status_code=303)

@app.post("/enclosures/delete/{enclosure_id}", response_class=HTMLResponse)
def delete_enclosure(request: Request, enclosure_id: int, db: Session = Depends(get_db)):
    enclosure = db.query(Enclosure).filter(Enclosure.id == enclosure_id).first()
    if not enclosure:
        raise HTTPException(status_code=404, detail="Enclosure not found")

    db.delete(enclosure)
    db.commit()
    return RedirectResponse(url="/enclosures", status_code=303)

# ------------------------------------------- ENCLOSURE ACCESS -----------------------------------------
class EnclosureAccess(Base):
    __tablename__ = 'enclosureaccess'

    enclosure_id = Column(Integer, ForeignKey('enclosure.id'), primary_key=True)
    employee_id = Column(Integer, ForeignKey('employee.id'), primary_key=True)

    enclosure = relationship("Enclosure", back_populates="access")
    employee = relationship("Employee", back_populates="access")


@app.get("/enclosure-access", response_class=HTMLResponse)
def read_enclosure_access(request: Request, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    access_list = db.query(EnclosureAccess).offset(skip).limit(limit).all()
    return templates.TemplateResponse("enclosure_access.html", {"request": request, "access_list": access_list})

@app.post("/enclosure-access/create", response_class=HTMLResponse)
def create_enclosure_access(
    request: Request,
    enclosure_id: int = Form(...),
    employee_id: int = Form(...),
    db: Session = Depends(get_db)
):
    access = EnclosureAccess(
        enclosure_id=enclosure_id,
        employee_id=employee_id,
    )
    db.add(access)
    db.commit()
    db.refresh(access)
    return RedirectResponse(url="/enclosure-access", status_code=303)

@app.post("/enclosure-access/delete/{enclosure_id}/{employee_id}", response_class=HTMLResponse)
def delete_enclosure_access(request: Request, enclosure_id: int, employee_id: int, db: Session = Depends(get_db)):
    access = db.query(EnclosureAccess).filter(EnclosureAccess.enclosure_id == enclosure_id, EnclosureAccess.employee_id == employee_id).first()
    if not access:
        raise HTTPException(status_code=404, detail="Access record not found")

    db.delete(access)
    db.commit()
    return RedirectResponse(url="/enclosure-access", status_code=303)


# ------------------------------------------- FOODS -----------------------------------------
class Food(Base):
    __tablename__ = 'foods'

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    
    supplies = relationship("Supply", back_populates="food")
    
@app.get("/foods", response_class=HTMLResponse)
def read_foods(request: Request, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    foods = db.query(Food).offset(skip).limit(limit).all()
    return templates.TemplateResponse("foods.html", {"request": request, "foods": foods})

@app.post("/foods/create", response_class=HTMLResponse)
def create_food(
    request: Request,
    type: str = Form(...),
    name: str = Form(...),
    db: Session = Depends(get_db)
):
    food = Food(
        type=type,
        name=name,
    )
    db.add(food)
    db.commit()
    db.refresh(food)
    return RedirectResponse(url="/foods", status_code=303)

@app.post("/foods/edit/{food_id}", response_class=HTMLResponse)
def edit_food(
    request: Request,
    food_id: int,
    type: str = Form(...),
    name: str = Form(...),
    db: Session = Depends(get_db)
):
    food = db.query(Food).filter(Food.id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    food.type = type
    food.name = name

    db.commit()
    db.refresh(food)
    return RedirectResponse(url="/foods", status_code=303)

@app.post("/foods/delete/{food_id}", response_class=HTMLResponse)
def delete_food(request: Request, food_id: int, db: Session = Depends(get_db)):
    food = db.query(Food).filter(Food.id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")

    db.delete(food)
    db.commit()
    return RedirectResponse(url="/foods", status_code=303)

# ------------------------------------------- SUPPLIES -----------------------------------------
class Supply(Base):
    __tablename__ = 'supplies'

    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer, ForeignKey('foods.id'), nullable=False)
    supplier_name = Column(String, nullable=False)

    food = relationship("Food", back_populates="supplies")

@app.get("/supplies", response_class=HTMLResponse)
def read_supplies(request: Request, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    supplies = db.query(Supply).offset(skip).limit(limit).all()
    return templates.TemplateResponse("supplies.html", {"request": request, "supplies": supplies})

@app.post("/supplies/create", response_class=HTMLResponse)
def create_supply(
    request: Request,
    food_id: int = Form(...),
    supplier_name: str = Form(...),
    db: Session = Depends(get_db)
):
    supply = Supply(
        food_id=food_id,
        supplier_name=supplier_name,
    )
    db.add(supply)
    db.commit()
    db.refresh(supply)
    return RedirectResponse(url="/supplies", status_code=303)

@app.post("/supplies/edit/{supply_id}", response_class=HTMLResponse)
def edit_supply(
    request: Request,
    supply_id: int,
    food_id: int = Form(...),
    supplier_name: str = Form(...),
    db: Session = Depends(get_db)
):
    supply = db.query(Supply).filter(Supply.id == supply_id).first()
    if not supply:
        raise HTTPException(status_code=404, detail="Supply not found")

    supply.food_id = food_id
    supply.supplier_name = supplier_name

    db.commit()
    db.refresh(supply)
    return RedirectResponse(url="/supplies", status_code=303)

@app.post("/supplies/delete/{supply_id}", response_class=HTMLResponse)
def delete_supply(request: Request, supply_id: int, db: Session = Depends(get_db)):
    supply = db.query(Supply).filter(Supply.id == supply_id).first()
    if not supply:
        raise HTTPException(status_code=404, detail="Supply not found")

    db.delete(supply)
    db.commit()
    return RedirectResponse(url="/supplies", status_code=303)
# ------------------------------------------- VET CARDS -----------------------------------------
class VetCard(Base):
    __tablename__ = 'vetcard'

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employee.id'))
    animal_id = Column(Integer, ForeignKey('animal.id'))
    current_diseases = Column(String(100))
    got_vaccination = Column(String(100))
    date = Column(Date)
    weight = Column(DECIMAL(5, 2))
    height = Column(DECIMAL(5, 2))

    # Relationships
    employee = relationship("Employee")
    animal = relationship("Animal")

@app.get("/vet-cards", response_class=HTMLResponse)
def read_vet_cards(request: Request, db: Session = Depends(get_db)):
    vet_cards = db.query(VetCard).all()
    return templates.TemplateResponse("vet_cards.html", {"request": request, "vet_cards": vet_cards})

# Create vet card
@app.post("/vet-cards/create", response_class=HTMLResponse)
def create_vet_card(
    request: Request,
    employee_id: int = Form(...),
    animal_id: int = Form(...),
    current_diseases: str = Form(None),
    got_vaccination: str = Form(...),
    date: str = Form(...),
    weight: float = Form(None),
    height: float = Form(None),
    db: Session = Depends(get_db)
):
    vet_card = VetCard(
        employee_id=employee_id,
        animal_id=animal_id,
        current_diseases=current_diseases,
        got_vaccination=got_vaccination,
        date=date,
        weight=weight,
        height=height
    )
    db.add(vet_card)
    db.commit()
    db.refresh(vet_card)
    return RedirectResponse(url="/vet-cards", status_code=303)

# Edit vet card
@app.post("/vet-cards/edit/{vet_card_id}", response_class=HTMLResponse)
def edit_vet_card(
    request: Request,
    vet_card_id: int,
    employee_id: int = Form(...),
    animal_id: int = Form(...),
    current_diseases: str = Form(None),
    got_vaccination: str = Form(...),
    date: str = Form(...),
    weight: float = Form(None),
    height: float = Form(None),
    db: Session = Depends(get_db)
):
    vet_card = db.query(VetCard).filter(VetCard.id == vet_card_id).first()
    if not vet_card:
        raise HTTPException(status_code=404, detail="Vet Card not found")

    vet_card.employee_id = employee_id
    vet_card.animal_id = animal_id
    vet_card.current_diseases = current_diseases
    vet_card.got_vaccination = got_vaccination
    vet_card.date = date
    vet_card.weight = weight
    vet_card.height = height

    db.commit()
    db.refresh(vet_card)
    return RedirectResponse(url="/vet-cards", status_code=303)

# Delete vet card
@app.post("/vet-cards/delete/{vet_card_id}", response_class=HTMLResponse)
def delete_vet_card(vet_card_id: int, db: Session = Depends(get_db)):
    vet_card = db.query(VetCard).filter(VetCard.id == vet_card_id).first()
    if not vet_card:
        raise HTTPException(status_code=404, detail="Vet Card not found")

    db.delete(vet_card)
    db.commit()
    return RedirectResponse(url="/vet-cards", status_code=303)

# ------------------------------------------- RATIONS -----------------------------------------
class Ration(Base):
    __tablename__ = 'ration'

    id = Column(Integer, primary_key=True, index=True)
    day_of_the_week = Column(String(10))
    time = Column(Time)
    food_id = Column(Integer, ForeignKey('foods.id'))
    animal_id = Column(Integer, ForeignKey('animal.id'))
    
    food = relationship("Food")
    animal = relationship("Animal")
    
# Read all rations
@app.get("/rations", response_class=HTMLResponse)
def read_rations(request: Request, db: Session = Depends(get_db)):
    rations = db.query(Ration).all()
    return templates.TemplateResponse("rations.html", {"request": request, "rations": rations})

# Create ration
@app.post("/rations/create", response_class=HTMLResponse)
def create_ration(
    request: Request,
    day_of_the_week: str = Form(...),
    time: str = Form(...),
    food_id: int = Form(...),
    animal_id: int = Form(...),
    db: Session = Depends(get_db)
):
    ration = Ration(
        day_of_the_week=day_of_the_week,
        time=time,
        food_id=food_id,
        animal_id=animal_id
    )
    db.add(ration)
    db.commit()
    db.refresh(ration)
    return RedirectResponse(url="/rations", status_code=303)

# Edit ration
@app.post("/rations/edit/{ration_id}", response_class=HTMLResponse)
def edit_ration(
    request: Request,
    ration_id: int,
    day_of_the_week: str = Form(...),
    time: str = Form(...),
    food_id: int = Form(...),
    animal_id: int = Form(...),
    db: Session = Depends(get_db)
):
    ration = db.query(Ration).filter(Ration.id == ration_id).first()
    if not ration:
        raise HTTPException(status_code=404, detail="Ration not found")

    ration.day_of_the_week = day_of_the_week
    ration.time = time
    ration.food_id = food_id
    ration.animal_id = animal_id

    db.commit()
    db.refresh(ration)
    return RedirectResponse(url="/rations", status_code=303)

# Delete ration
@app.post("/rations/delete/{ration_id}", response_class=HTMLResponse)
def delete_ration(ration_id: int, db: Session = Depends(get_db)):
    ration = db.query(Ration).filter(Ration.id == ration_id).first()
    if not ration:
        raise HTTPException(status_code=404, detail="Ration not found")

    db.delete(ration)
    db.commit()
    return RedirectResponse(url="/rations", status_code=303)

# ------------------------------------------- ANIMAL COMPATABILITY -----------------------------------------
class AnimalCompatibility(Base):
    __tablename__ = 'animalcompatibility'

    id = Column(Integer, primary_key=True, index=True)
    first_species = Column(String(50))
    second_species = Column(String(50))
    is_compatible = Column(Boolean)
    
    
# Read all animal compatibilities
@app.get("/animal-compatibilities", response_class=HTMLResponse)
def read_animal_compatibilities(request: Request, db: Session = Depends(get_db)):
    compatibilities = db.query(AnimalCompatibility).all()
    return templates.TemplateResponse("animal_compatibilities.html", {"request": request, "compatibilities": compatibilities})

# Create animal compatibility
@app.post("/animal-compatibilities/create", response_class=HTMLResponse)
def create_animal_compatibility(
    request: Request,
    first_species: str = Form(...),
    second_species: str = Form(...),
    is_compatible: bool = Form(...),
    db: Session = Depends(get_db)
):
    compatibility = AnimalCompatibility(
        first_species=first_species,
        second_species=second_species,
        is_compatible=is_compatible
    )
    db.add(compatibility)
    db.commit()
    db.refresh(compatibility)
    return RedirectResponse(url="/animal-compatibilities", status_code=303)

# Edit animal compatibility
@app.post("/animal-compatibilities/edit/{compatibility_id}", response_class=HTMLResponse)
def edit_animal_compatibility(
    request: Request,
    compatibility_id: int,
    first_species: str = Form(...),
    second_species: str = Form(...),
    is_compatible: bool = Form(...),
    db: Session = Depends(get_db)
):
    compatibility = db.query(AnimalCompatibility).filter(AnimalCompatibility.id == compatibility_id).first()
    if not compatibility:
        raise HTTPException(status_code=404, detail="Animal Compatibility not found")

    compatibility.first_species = first_species
    compatibility.second_species = second_species
    compatibility.is_compatible = is_compatible

    db.commit()
    db.refresh(compatibility)
    return RedirectResponse(url="/animal-compatibilities", status_code=303)

# Delete animal compatibility
@app.post("/animal-compatibilities/delete/{compatibility_id}", response_class=HTMLResponse)
def delete_animal_compatibility(compatibility_id: int, db: Session = Depends(get_db)):
    compatibility = db.query(AnimalCompatibility).filter(AnimalCompatibility.id == compatibility_id).first()
    if not compatibility:
        raise HTTPException(status_code=404, detail="Animal Compatibility not found")

    db.delete(compatibility)
    db.commit()
    return RedirectResponse(url="/animal-compatibilities", status_code=303)

# ------------------------------------------- TASK 1 -----------------------------------------
# Route to get employees based on filters
@app.get("/task1", response_class=HTMLResponse)
def task1(
    request: Request,
    min_age: int = Query(None, alias="min_age"),
    min_salary: float = Query(None, alias="min_salary"),
    position: str = Query(None),
    sex: str = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Employee)

    if min_age is not None:
        query = query.filter(Employee.age >= min_age)
    else:
        min_age = 0  # Set default value if min_age is None

    if min_salary is not None:
        query = query.filter(Employee.salary >= min_salary)
    else:
        min_salary = 0.0  # Set default value if min_salary is None

    if position:
        query = query.filter(Employee.position == position)

    if sex:
        query = query.filter(Employee.sex == sex)

    employees = query.all()
    total_count = query.count()

    return templates.TemplateResponse("task1.html", {"request": request, "employees": employees, "total_count": total_count})
# ------------------------------------------- TASK 2 -----------------------------------------
@app.get("/task2", response_class=HTMLResponse)
def task2(
    request: Request,
    animal_id: Optional[int] = Query(None, alias="animal_id"),
    start_date: Optional[date] = Query(None, alias="start_date"),
    end_date: Optional[date] = Query(None, alias="end_date"),
    db: Session = Depends(get_db)
):
    query = db.query(Employee).join(VetCard)

    if animal_id:
        query = query.filter(VetCard.animal_id == animal_id)

    if start_date and end_date:
        query = query.filter(VetCard.date >= start_date, VetCard.date <= end_date)

    employees = query.all()
    total_count = query.count()

    return templates.TemplateResponse("task2.html", {"request": request, "employees": employees, "total_count": total_count})
# ------------------------------------------- TASK 3 -----------------------------------------
@app.get("/task3", response_class=HTMLResponse)
def task3(
    request: Request,
    animal_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    if animal_id is None:
        animal_id = 1
        
    # Get enclosure for the given animal_id
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail=f"Animal with id {animal_id} not found")

    enclosure_id = animal.enclosure_id
    
    # Get employees with access to this enclosure
    employees = db.query(Employee).join(EnclosureAccess).filter(EnclosureAccess.enclosure_id == enclosure_id).all()
    total_count = len(employees)

    return templates.TemplateResponse("task3.html", {"request": request, "employees": employees, "total_count": total_count})
# ------------------------------------------- TASK 4 -----------------------------------------
def calculate_age(birthdate):
    today = date.today()
    return today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

@app.get("/task4", response_class=HTMLResponse)
def task4(
    request: Request,
    species: Optional[str] = None,
    enclosure_id: Optional[int] = Query(None, alias="enclosure_id"),
    gender: Optional[str] = None,
    min_age: Optional[int] = Query(None, alias="min_age"),
    max_age: Optional[int] = Query(None, alias="max_age"),
    min_weight: Optional[float] = Query(None, alias="min_weight"),
    max_weight: Optional[float] = Query(None, alias="max_weight"),
    min_height: Optional[float] = Query(None, alias="min_height"),
    max_height: Optional[float] = Query(None, alias="max_height"),
    db: Session = Depends(get_db)
):
    # Subquery to get the latest vet card entry for each animal
    latest_vetcard_subquery = db.query(
        VetCard.animal_id,
        func.max(VetCard.date).label('max_date')
    ).group_by(VetCard.animal_id).subquery()

    VetCardAlias = aliased(VetCard)

    query = db.query(Animal, VetCardAlias).join(
        latest_vetcard_subquery,
        Animal.id == latest_vetcard_subquery.c.animal_id
    ).join(
        VetCardAlias,
        and_(
            Animal.id == VetCardAlias.animal_id,
            VetCardAlias.date == latest_vetcard_subquery.c.max_date
        )
    )

    if species:
        query = query.filter(Animal.species == species)
    
    if enclosure_id and enclosure_id != 0:
        query = query.filter(Animal.enclosure_id == enclosure_id)
    
    if gender:
        query = query.filter(Animal.gender == gender)
    
    animals = query.all()

    # Filter animals by age, weight, and height
    filtered_animals = []
    for animal, vetcard in animals:
        age = calculate_age(animal.date_of_birth)
        if min_age and min_age != 0 and age < min_age:
            continue
        if max_age and max_age != 0 and age > max_age:
            continue
        if min_weight and min_weight != 0 and vetcard.weight < min_weight:
            continue
        if max_weight and max_weight != 0 and vetcard.weight > max_weight:
            continue
        if min_height and min_height != 0 and vetcard.height < min_height:
            continue
        if max_height and max_height != 0 and vetcard.height > max_height:
            continue
        filtered_animals.append((animal, vetcard))
    
    total_count = len(filtered_animals)
    
    return templates.TemplateResponse("task4.html", {"request": request, "animals": filtered_animals, "total_count": total_count})
# ------------------------------------------- TASK 5 -----------------------------------------
@app.get("/task5", response_class=HTMLResponse)
def task5(
    request: Request,
    species: Optional[str] = None,
    min_age: Optional[int] = Query(None, alias="min_age"),
    max_age: Optional[int] = Query(None, alias="max_age"),
    db: Session = Depends(get_db)
):
    # Create the base query
    query = db.query(Animal).filter(Animal.needs_heated_enclosure_for_winter == True)

    # Apply filters if they are provided
    if species:
        query = query.filter(Animal.species == species)
    
    if min_age and min_age != 0:
        query = query.filter(func.date_part('year', func.age(Animal.date_of_birth)) >= min_age)
    
    if max_age and max_age != 0:
        query = query.filter(func.date_part('year', func.age(Animal.date_of_birth)) <= max_age)
    
    # Execute the query
    animals = query.all()
    total_count = len(animals)

    current_year = datetime.now().year

    return templates.TemplateResponse("task5.html", {"request": request, "animals": animals, "total_count": total_count, "current_year": current_year})
# ------------------------------------------- TASK 6 -----------------------------------------
# ------------------------------------------- TASK 7 -----------------------------------------
# ------------------------------------------- TASK 8 -----------------------------------------
# ------------------------------------------- TASK 9 -----------------------------------------
# ------------------------------------------- TASK 10 -----------------------------------------
# ------------------------------------------- TASK 11 -----------------------------------------
# ------------------------------------------- TASK 12 -----------------------------------------
# ------------------------------------------- TASK 13 -----------------------------------------
# ------------------------------------------- TASK 14 -----------------------------------------
# ------------------------------------------- TASK 15 -----------------------------------------