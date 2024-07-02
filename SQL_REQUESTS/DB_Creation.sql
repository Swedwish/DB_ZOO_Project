CREATE TABLE titles(
	job_title varchar(128) PRIMARY KEY NOT NULL,
	can_access_cells bool DEFAULT FALSE,
	description varchar(128)
);

CREATE TABLE worker(
	id serial PRIMARY KEY,
	name varchar(128) NOT NULL,
	date_of_birth date,
	salary int,
	job_title varchar(128) NOT NULL,
	gender varchar(8),
	FOREIGN KEY (job_title) REFERENCES titles(job_title)
);


CREATE TABLE cell(
	id int PRIMARY KEY NOT NULL,
	size_m3 int,
	average_temperature int
);

CREATE TABLE animal(
	id serial PRIMARY KEY NOT NULL,
	name varchar(128),
	species varchar(128) NOT NULL,
	date_of_birth date,
	gender varchar(8),
	cell_id int,
	FOREIGN KEY (cell_id) REFERENCES cell(id)
);

CREATE TABLE job(
	id serial PRIMARY KEY NOT NULL,
	worker_id int NOT NULL,
	animal_id int NOT NULL,
	job_description varchar(64),
	FOREIGN KEY (worker_id) REFERENCES worker(id),
	FOREIGN KEY (animal_id) REFERENCES animal(id)
);

CREATE TABLE food_types(
	f_type varchar(64) PRIMARY KEY NOT NULL,
	f_class varchar(64) NOT NULL
);

CREATE TABLE food(
	name varchar(256) NOT NULL UNIQUE,
	kcalories int,
	f_type varchar(64) NOT NULL,
	FOREIGN KEY (f_type) REFERENCES food_types(f_type)
);


CREATE TABLE diet(
	id serial PRIMARY KEY NOT NULL,
	animal_id int NOT NULL ,
	food_name varchar(64) NOT NULL,
	amount_kg int,
	FOREIGN KEY(animal_id) REFERENCES  animal(id),
	FOREIGN KEY(food_name) REFERENCES  food(name)
);


CREATE TABLE food_retailer(
	id serial PRIMARY KEY NOT NULL,
	name varchar(256) NOT NULL,
	food_name varchar(256) NOT NULL,
	price int NOT NULL,
	FOREIGN KEY(food_name) REFERENCES food(name)
);

