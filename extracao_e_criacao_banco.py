import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, select, Text,text
import pymysql
import re
import requests
from bs4 import BeautifulSoup
from tratamento_dicionario import receber_url
from getpass import getpass


# 1. Função para extrair nome limpo da região e notas (sem notas numéricas)
def split_region_and_notes(text):
    if pd.isna(text):
        return '', []
    notes = re.findall(r'\[.*?\]', text)
    clean_notes = []
    for note in notes:
        tag = note.strip('[]').strip()
        if not tag.isdigit():  # filtra referências numéricas
            clean_notes.append(tag)
    name = re.split(r'\[', text)[0].strip()
    return name, clean_notes

# 2. Função para extrair número e notas não numéricas nas colunas numéricas
def clean_number_and_notes(val):
    if pd.isna(val):
        return 0, []
    notes = re.findall(r'\[.*?\]', str(val))
    clean_notes = []
    for note in notes:
        tag = note.strip('[]').strip()
        if not tag.isdigit():
            clean_notes.append(tag)
    try:
        number = int(str(val).split('[')[0])
    except:
        number = 0
    return number, clean_notes


# 3. Leitura da tabela UNESCO da Wikipedia
url = 'https://en.wikipedia.org/wiki/List_of_World_Heritage_Sites_by_country'
tables = pd.read_html(url)
unesco_df = tables[0]

note_descriptions: dict = receber_url(url)


# 5. Renomear colunas e remover linha Total
unesco_df.columns = ['Country', 'Cultural', 'Natural', 'Mixed', 'Total', 'Shared', 'Region']
unesco_df = unesco_df[unesco_df['Country'] != 'Total'].copy()

# 6. Extrai dados e notas das colunas numéricas
for col in ['Cultural', 'Natural', 'Mixed']:
    unesco_df[[f'{col}_count', f'{col}_notes']] = unesco_df[col].apply(lambda x: pd.Series(clean_number_and_notes(x)))

# 7. Extrai região limpa e notas (sem referências numéricas)
unesco_df[['Region_clean', 'Region_notes']] = unesco_df['Region'].apply(lambda x: pd.Series(split_region_and_notes(x)))

meaningful_notes = {}
numeric_references = {}

for tag, content in note_descriptions.items():
    if tag.isdigit():  # These are just numeric citation markers
        numeric_references[tag] = content
    else:
        meaningful_notes[tag] = content

# print(f"Found {len(meaningful_notes)} meaningful notes")
# print(f"Found {len(numeric_references)} numeric references (can be ignored)")

# Solicita credenciais ao usuário
print('\n[Geração do Banco de dados ] \n')
usuario = input("Informe o nome de usuário do MySQL: ")
senha = getpass("Informe a senha: ")
host = input("Informe o host (padrão: localhost): ") or "localhost"
porta = input("Informe a porta (padrão: 3306): ") or "3306"
nome_banco = input("Informe o nome do banco de dados: ")

# Cria a engine para conexão com o banco especificado
url_conexao = f"mysql+pymysql://{usuario}:{senha}@{host}:{porta}/{nome_banco}"

# Conecta ao MySQL sem especificar o banco de dados
url_inicial = f"mysql+pymysql://{usuario}:{senha}@{host}:{porta}/"

engine_inicial= create_engine(url_inicial)

# Cria o banco se não existir
with engine_inicial.connect() as conn:
    conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {nome_banco}"))
    print(f"Banco '{nome_banco}' verificado ou criado com sucesso!")

engine = create_engine(f"mysql+pymysql://{usuario}:{senha}@{host}:{porta}/{nome_banco}")

metadata = MetaData()

# 9. Definição das tabelas
regions = Table('regions', metadata,
                Column('id_regions', Integer, primary_key=True, autoincrement=True),
                Column('name', String(100), unique=True, nullable=False))

countries = Table('countries', metadata,
                  Column('id_countries', Integer, primary_key=True, autoincrement=True),
                  Column('name', String(100), unique=True, nullable=False),
                  Column('region_id', Integer, ForeignKey('regions.id_regions')))

site_types = Table('site_types', metadata,
                   Column('id_site_types', Integer, primary_key=True, autoincrement=True),
                   Column('type_name', String(50), unique=True, nullable=False))

heritage_sites_counts = Table('heritage_sites_counts', metadata,
                              Column('id_heritage_sites', Integer, primary_key=True, autoincrement=True),
                              Column('country_id', Integer, ForeignKey('countries.id_countries')),
                              Column('site_type_id', Integer, ForeignKey('site_types.id_site_types')),
                              Column('site_count', Integer, default=0))

notes = Table('notes', metadata,
              Column('id_note', Integer, primary_key=True, autoincrement=True),
              Column('tag', String(50), unique=True, nullable=False),
              Column('description', Text))

region_notes = Table('region_notes', metadata,
                     Column('id_region_note', Integer, primary_key=True, autoincrement=True),
                     Column('region_id', Integer, ForeignKey('regions.id_regions')),
                     Column('note_id', Integer, ForeignKey('notes.id_note')))

country_notes = Table('country_notes', metadata,
                      Column('id_country_note', Integer, primary_key=True, autoincrement=True),
                      Column('country_id', Integer, ForeignKey('countries.id_countries')),
                      Column('note_id', Integer, ForeignKey('notes.id_note')),
                      Column('site_type_id', Integer, ForeignKey('site_types.id_site_types')))




#10. Criar tabelas no banco
metadata.create_all(engine)

# 11. Inserção de dados
with engine.begin() as conn:
    
    # Inserido todas notações necessárias
    for tag, description in meaningful_notes.items():
        # Verifica caso já exista notas no banco
        exists = conn.execute(
            select(notes.c.id_note).where(notes.c.tag == tag)
        ).fetchone()
        
        if not exists:
            # Inserção de notas
            conn.execute(
                notes.insert().values(
                    tag=tag,
                    description=description
                )
            )
            print(f"Inserted note {tag}")
        else:
            print(f"Note {tag} already exists, skipping")

    sample_notes = conn.execute(
        select(notes).limit(5)
    ).fetchall()
    
    # Inserir tipos de sítio
    site_types_data = ['Cultural', 'Natural', 'Mixed']
    site_type_map = {}
    for stype in site_types_data:
        result = conn.execute(select(site_types.c.id_site_types).where(site_types.c.type_name == stype)).fetchone()
        if result:
            site_type_id = result[0]
        else:
            conn.execute(site_types.insert().values(type_name=stype))
            site_type_id = conn.execute(select(site_types.c.id_site_types).where(site_types.c.type_name == stype)).fetchone()[0]
        site_type_map[stype] = site_type_id

    # Inserir regiões
    region_map = {}
    for reg in unesco_df['Region_clean'].unique():
        result = conn.execute(select(regions.c.id_regions).where(regions.c.name == reg)).fetchone()
        if result:
            region_id = result[0]
        else:
            conn.execute(regions.insert().values(name=reg))
            region_id = conn.execute(select(regions.c.id_regions).where(regions.c.name == reg)).fetchone()[0]
        region_map[reg] = region_id

    # Inserir notas globais e criar mapa (com descrição da extração)
    note_map = {}
    # Notas da região
    for note_list in unesco_df['Region_notes']:
        for note in note_list:
            if note not in note_map:
                result = conn.execute(select(notes.c.id_note).where(notes.c.tag == note)).fetchone()
                if result:
                    note_id = result[0]
                else:
                    description = note_descriptions.get(note, None)
                    conn.execute(notes.insert().values(tag=note, description=description))
                    note_id = conn.execute(select(notes.c.id_note).where(notes.c.tag == note)).fetchone()[0]
                note_map[note] = note_id

    # Notas das colunas numéricas
    for col in ['Cultural_notes', 'Natural_notes', 'Mixed_notes']:
        for note_list in unesco_df[col]:
            for note in note_list:
                if note not in note_map:
                    result = conn.execute(select(notes.c.id_note).where(notes.c.tag == note)).fetchone()
                    if result:
                        note_id = result[0]
                    else:
                        description = note_descriptions.get(note, None)
                        conn.execute(notes.insert().values(tag=note, description=description))
                        note_id = conn.execute(select(notes.c.id_note).where(notes.c.tag == note)).fetchone()[0]
                    note_map[note] = note_id

    # Inserir países, contagens, notas regionais e notas específicas país+tipo
    for _, row in unesco_df.iterrows():
        region_id = region_map[row['Region_clean']]
        country_result = conn.execute(select(countries.c.id_countries).where(countries.c.name == row['Country'])).fetchone()
        if country_result:
            country_id = country_result[0]
        else:
            conn.execute(countries.insert().values(name=row['Country'], region_id=region_id))
            country_id = conn.execute(select(countries.c.id_countries).where(countries.c.name == row['Country'])).fetchone()[0]

        # Inserir contagens e notas por tipo
        for stype in site_types_data:
            count = row[f'{stype}_count']
            conn.execute(heritage_sites_counts.insert().values(
                country_id=country_id,
                site_type_id=site_type_map[stype],
                site_count=count
            ))

            note_list = row[f'{stype}_notes']
            for note in note_list:
                note_id = note_map.get(note)
                if note_id:
                    # Evitar duplicidade opcional
                    exists = conn.execute(select(country_notes).where(
                        (country_notes.c.country_id == country_id) &
                        (country_notes.c.note_id == note_id) &
                        (country_notes.c.site_type_id == site_type_map[stype])
                    )).fetchone()
                    if not exists:
                        conn.execute(country_notes.insert().values(
                            country_id=country_id,
                            note_id=note_id,
                            site_type_id=site_type_map[stype]
                        ))

        # Inserir notas da região (se quiser manter)
        for note in row['Region_notes']:
            conn.execute(region_notes.insert().values(
                region_id=region_id,
                note_id=note_map[note]
            ))

print("✅ Inserção completa com notas e descrições filtradas (sem referências numéricas)!")
