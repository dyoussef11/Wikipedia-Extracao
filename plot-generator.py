import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
import os

# Conectar ao banco de dados MySQL
db_user = os.getenv('DB_USER', 'user')
db_pass = os.getenv('DB_PASS', 'pass')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '3305')
db_name = os.getenv('DB_NAME', 'mydb')

connection_string = f'mysql+pymysql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'
engine = create_engine(connection_string)

# Create output directory for saved images if it doesn't exist
output_dir = 'plots'
os.makedirs(output_dir, exist_ok=True)

# Consultas SQL
queries = {
    "sítios por tipo e região": """
        SELECT r.name AS region, s.type_name, SUM(h.site_count) AS total
        FROM site_types s
        JOIN heritage_sites_counts h ON h.site_type_id = s.id_site_types
        JOIN countries c ON c.id_countries = h.country_id
        JOIN regions r ON c.region_id = r.id_regions
        GROUP BY r.name, s.type_name;
    """,
    "total de sítios por país": """
        SELECT c.name AS country, SUM(h.site_count) AS total_sites
        FROM countries c
        JOIN heritage_sites_counts h ON c.id_countries = h.country_id
        GROUP BY c.name;
    """,
    "países europeus com mais de 10 sítios": """
        SELECT c.name AS country, SUM(h.site_count) AS total_sites
        FROM regions r
        JOIN countries c ON c.region_id = r.id_regions
        JOIN heritage_sites_counts h ON c.id_countries = h.country_id
        WHERE r.name LIKE '%%Europe%%' 
        GROUP BY c.name
        HAVING total_sites > 10
        ORDER BY total_sites DESC;
    """,
    "países sem sítios mistos": """
        SELECT DISTINCT c.name AS country
        FROM countries c
        JOIN heritage_sites_counts h ON c.id_countries = h.country_id
        WHERE c.id_countries NOT IN (
            SELECT h.country_id
            FROM heritage_sites_counts h
            JOIN site_types s ON s.id_site_types = h.site_type_id
            WHERE s.type_name = 'Mixed' AND h.site_count > 0
        );
    """,
    "regiões com mais sítios": """
        SELECT r.name AS region, SUM(h.site_count) AS total_sites
        FROM regions r
        JOIN countries c ON c.region_id = r.id_regions
        JOIN heritage_sites_counts h ON c.id_countries = h.country_id
        GROUP BY r.name
        ORDER BY total_sites DESC;
    """
}

# Criar gráficos para cada consulta
figures = {}
saved_files = []

for title, query in queries.items():
    df = pd.read_sql_query(query, engine)
    
    fig = plt.figure(figsize=(14, 10))  # Even larger figure size
    
    if 'region' in df.columns and 'type_name' in df.columns:
        sns.barplot(data=df, x="region", y="total", hue="type_name")
        plt.title("Sítios por Tipo e Região")
        plt.xticks(rotation=45, ha='right')  # Added horizontal alignment
        # Give more space at the bottom for rotated labels
        plt.subplots_adjust(bottom=0.25)
    elif 'country' in df.columns and 'total_sites' in df.columns:
        top_df = df.sort_values(by='total_sites', ascending=False).head(15)
        sns.barplot(data=top_df, x="total_sites", y="country", hue="country", palette="viridis", legend=False)
        plt.title(title)
        # Standard margins are usually fine for horizontal bar charts
        plt.subplots_adjust(left=0.3)  # More space for country names
    elif 'region' in df.columns and 'total_sites' in df.columns:
        sns.barplot(data=df, x="total_sites", y="region", hue="region", palette="mako", legend=False)
        plt.title(title)
        # Standard margins are usually fine for horizontal bar charts
        plt.subplots_adjust(left=0.3)  # More space for region names
    elif 'country' in df.columns and len(df.columns) == 1:
        plt.axis('off')
        text = '\n'.join(df['country'].tolist())
        plt.text(0.01, 0.8, f"Países sem sítios mistos:\n\n{text}", fontsize=12)
    else:
        plt.close(fig)
        continue
    
    # Save the figure to a file
    filename = os.path.join(output_dir, f"{title.replace(' ', '_')}.png")
    fig.savefig(filename, dpi=300, bbox_inches='tight')
    saved_files.append(filename)
    
    figures[title] = fig
    plt.close(fig)

print("Images saved to the following locations:")
for filename in saved_files:
    print(f"- {filename}")

print("\nAvailable figures:", list(figures.keys()))