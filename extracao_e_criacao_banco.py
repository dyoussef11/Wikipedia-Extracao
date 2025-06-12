import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, select
import pymysql

# 1. Leitura da tabela UNESCO
url = 'https://en.wikipedia.org/wiki/List_of_World_Heritage_Sites_by_country'
tables = pd.read_html(url)
unesco_df = tables[0]

print(f'[Antes da Limpeza]: \n\n',unesco_df)
# # 2. Limpeza dos dados
unesco_df.columns = ['Country', 'Cultural', 'Natural', 'Mixed', 'Total', 'Shared', 'Region']
print(f'[Depois da Renomear]: \n\n',unesco_df)
unesco_df = unesco_df[unesco_df['Country'] != 'Total']  # Remove totalizador

def clean_number(val):
    try:
        return int(str(val).split('[')[0])
    except:
        return 0

for col in ['Cultural', 'Natural', 'Mixed']:
    unesco_df.loc[:, col] = unesco_df[col].map(clean_number)

print(f'[Depois da Limpeza]: \n\n',unesco_df)

# 3. Conexão com MySQL
engine = create_engine('mysql+pymysql://usuario:1234@localhost:3306/unesco_db')
metadata = MetaData()

# 4. Definição das tabelas
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


# 5. Criar tabelas no banco
metadata.create_all(engine)

# 6. Inserção de dados
with engine.begin() as conn:
    print("🔄 Inserindo tipos de site (site_types)...")
    site_types_data = ['Cultural', 'Natural', 'Mixed']
    site_type_map = {}
    for stype in site_types_data:
        sel = select(site_types.c.id_site_types).where(site_types.c.type_name == stype)
        result = conn.execute(sel).fetchone()
        if result:
            site_type_id = result[0]
            print(f" - Tipo '{stype}' já existe com id {site_type_id}")
        else:
            conn.execute(site_types.insert().values(type_name=stype))
            site_type_id = conn.execute(select(site_types.c.id_site_types).where(site_types.c.type_name == stype)).fetchone()[0]
            print(f" - Tipo '{stype}' inserido com id {site_type_id}")
        site_type_map[stype] = site_type_id

    print("\n🔄 Inserindo regiões (regions)...")
    region_map = {}
    for reg in unesco_df['Region'].unique():
        sel = select(regions.c.id_regions).where(regions.c.name == reg)
        result = conn.execute(sel).fetchone()
        if result:
            region_id = result[0]
            print(f" - Região '{reg}' já existe com id {region_id}")
        else:
            conn.execute(regions.insert().values(name=reg))
            region_id = conn.execute(select(regions.c.id_regions).where(regions.c.name == reg)).fetchone()[0]
            print(f" - Região '{reg}' inserida com id {region_id}")
        region_map[reg] = region_id

    print("\n🔄 Inserindo países e contagens...")
    for _, row in unesco_df.iterrows():
        region_id = region_map[row['Region']]

        sel = select(countries.c.id_countries).where(countries.c.name == row['Country'])
        result = conn.execute(sel).fetchone()
        if result:
            country_id = result[0]
            print(f" - País '{row['Country']}' já existe com id {country_id}")
        else:
            conn.execute(countries.insert().values(name=row['Country'], region_id=region_id))
            country_id = conn.execute(select(countries.c.id_countries).where(countries.c.name == row['Country'])).fetchone()[0]
            print(f" - País '{row['Country']}' inserido com id {country_id}")

        for stype in site_types_data:
            conn.execute(heritage_sites_counts.insert().values(
                country_id=country_id,
                site_type_id=site_type_map[stype],
                site_count=row[stype]
            ))
            print(f"   > Contagem inserida: país_id={country_id}, tipo='{stype}', contagem={row[stype]}")

        
print("✅ Dados inseridos com sucesso no MySQL!")
