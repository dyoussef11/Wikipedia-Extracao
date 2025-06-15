


# 🌍 Trabalho Prático de Normalização e alimentação banco de Dados - Sítios do Patrimônio Mundial da UNESCO

Este trabalho realiza a **extração, normalização e visualização** de dados sobre os Sítios do Patrimônio Mundial da UNESCO, com base em informações da Wikipedia. O objetivo é aplicar boas práticas de modelagem relacional e gerar gráficos a partir de consultas SQL sobre o banco estruturado.

---

## ⚙️ Requisitos

- Python 3.9+
- MySQL ou SQLite instalado (ou adaptável conforme necessidade)
- Ambiente virtual Python (recomendado)

---

## 📦 Instalação

Clone este repositório e, no terminal:

```bash
# Crie e ative um ambiente virtual (opcional, mas recomendado)
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows

# Instale as dependências
pip install -r requirements.txt
````

---

## 🚀 Execução

### 1. Criação e popularização do banco de dados

Execute o script responsável por **extrair os dados da Wikipedia, estruturar e popular o banco de dados**:

```bash
python extracao_e_criacao_banco.py
```

Esse script irá:

* Ler e limpar os dados da Wikipedia.
* Criar as tabelas normalizadas usando SQLAlchemy.
* Inserir os dados no banco relacional.

### 2. Geração dos gráficos SQL

**Apenas após a execução e sucesso do passo anterior**, rode o script de geração de gráficos a partir de consultas SQL ao banco criado:

```bash
python plot-generator.py
```

Esse script executa consultas e plota gráficos com base nas informações processadas.

---

## 🧱 Modelo Lógico Utilizado

• Regions (`id_regions`, `name`)
• Countries (`id_countries`, `name`, `region_id`)<br>
 region\_id referencia Regions

• Site\_types (`id_site_types`, `type_name`)

• Heritage\_sites\_counts (`id_heritage_sites`, `country_id`, `site_type_id`, `site_count`)<br>
country\_id referencia Countries<br>
site\_type\_id referencia Site\_types

• Notes (`id_note`, `tag`, `description`)

• Region\_notes (`id_region_note`, `region_id`, `note_id`)
region\_id referencia Regions<br>
note\_id referencia Notes<br>

• Country\_notes (`id_country_note`, `country_id`, `note_id`, `site_type_id`)
country\_id referencia Countries<br>
note\_id referencia Notes<br>
site\_type\_id referencia Site\_types<br>

---

## 📊 Exemplos de Gráficos Gerados

* Distribuição de tipos de sítios por país
* Total de sítios por região
* Comparações entre países com mais patrimônios naturais e culturais

---

## 📁 Estrutura do Projeto

```
📦wikipedia-Extracao
 ┣ 📄 README.md
 ┣ 📄 requirements.txt
 ┣ 📄 extracao_e_criacao_banco.py
 ┣ 📄 plot-generator.py
 ┣ 📄 tratamento_dicionario.py
 ┣ 📄 Consultas-SQL.sql
 ┣ 📄 Consultas-SQL.sql
 ┣ 📄 unesco_db.sql
 ┣ 📄 unesco_sites.csv 
 ┣ 📁 graficos
 ┃ ┗ 📄 fotos.png 
 ┣ 📁 Apresentação
 ┃ ┗ 📄 Apresentação - Trabalho Prático - Daniel,Victória e Gustavo.pdf
 ┃ ┗ 📄 Apresentação - Trabalho Prático - Daniel,Victória e Gustavo.pptx
 ┣ 📁 Diagramas - ER e Lógico
 ┃ ┗ 📄 Diagrama ER - Banco de dados .png
 ┃ ┗ 📄 unesco_db - Pela perceptiva do DBeaver.png
```

---

## 🧠 Autores

**Daniel Youssef**, **Victória Lik** e **Gustavo Dutra**<br>
Engenharia da Computação – UFSM
---
