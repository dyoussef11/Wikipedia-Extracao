-- Criação do banco de dados
CREATE DATABASE unesco2_db;

-- Seleciona o banco para uso (em MySQL ou MariaDB; no PostgreSQL você deve conectar com \c unesco_db)
USE unesco2_db;

-- Tabela de regiões
CREATE TABLE regions (
    id_regions INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL
);

-- Tabela de países
CREATE TABLE countries (
    id_countries INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    region_id INTEGER,
    FOREIGN KEY (region_id) REFERENCES regions(id_regions)
);

-- Tabela de tipos de sítios
CREATE TABLE site_types (
    id_site_types INTEGER PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(50) UNIQUE NOT NULL
);

-- Tabela com contagem de sítios por país e tipo
CREATE TABLE heritage_sites_counts (
    id_heritage_sites INTEGER PRIMARY KEY AUTO_INCREMENT,
    country_id INTEGER,
    site_type_id INTEGER,
    site_count INTEGER DEFAULT 0,
    FOREIGN KEY (country_id) REFERENCES countries(id_countries),
    FOREIGN KEY (site_type_id) REFERENCES site_types(id_site_types)
);

-- Tabela de notas (referências da Wikipedia, por exemplo)
CREATE TABLE notes (
    id_note INTEGER PRIMARY KEY AUTO_INCREMENT,
    tag VARCHAR(50) UNIQUE NOT NULL,
    description TEXT
);

-- Tabela associativa entre regiões e notas
CREATE TABLE region_notes (
    id_region_note INTEGER PRIMARY KEY AUTO_INCREMENT,
    region_id INTEGER,
    note_id INTEGER,
    FOREIGN KEY (region_id) REFERENCES regions(id_regions),
    FOREIGN KEY (note_id) REFERENCES notes(id_note)
);

-- Tabela associativa entre países, tipos de sítios e notas
CREATE TABLE country_notes (
    id_country_note INTEGER PRIMARY KEY AUTO_INCREMENT,
    country_id INTEGER,
    note_id INTEGER,
    site_type_id INTEGER,
    FOREIGN KEY (country_id) REFERENCES countries(id_countries),
    FOREIGN KEY (note_id) REFERENCES notes(id_note),
    FOREIGN KEY (site_type_id) REFERENCES site_types(id_site_types)
);
