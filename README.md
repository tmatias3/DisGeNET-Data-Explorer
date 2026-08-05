# DisGeNET Cube — Web Platform

> Infrastructure Note:
> This project was developed as part of a Database Systems university course, connected to an institutional SQL Server Data Warehouse. As the academic semester has concluded, the live database is no longer accessible, and consequently, the 'Search' and 'Statistics' pages are currently non-functional. The source code is provided here to demonstrate the ETL logic, system architecture, and UI/UX design implementation.

## Pages

| URL | Page | Description |
|-----|------|-------------|
| `/` | About | Project description, authors, cube schema general view and quick help |
| `/search/` | Search | Disease search using different filters |
| `/disease/<disease_id>/` | Disease detail | Detailed information about a disease: main genes, sources and gene-disease association per year. Accessible from the 'Search' page. Example: `/disease/C1861357/?next=/search/` |
| `/stats/` | Statistics | Different graphical statistics |

> The optional parameter ?next= defines the destination of the "back" button (e.g., ?next=/search/).

## Installation

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

> Note: mssql-django requires the ODBC Driver 18 for SQL Server to be installed on your system.
> Download it here: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### 2. Database configuration
Edit the `disgenet_project/settings.py` file and update the `DATABASES` section:

```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'team_06',
        'USER': 'team_06',
        'PASSWORD': 'a_tua_password',
        'HOST': 'o_teu_servidor',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 18 for SQL Server',
            'extra_params': 'TrustServerCertificate=yes',
        },
    }
}
```

> Note: Since the server used in this project was disabled, the database configuration was changed to allow landing page design visualization using the following code:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 3. Note on models and migrations

The models are set with `managed = False` — Django **will never create or modify** the cube's tables.
**Do not run** `makemigrations` for the `disgenet_app`. The tables already exist in the SQL Server.

If Django prompts for migrations during the first run, execute:

```bash
python manage.py migrate --run-syncdb
```

### 4. Run the development server

Ensure your working directory is`DisGeNET-Data-Explorer-main`.

```bash
cd DisGeNET-Data-Explorer-main
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

### 5. Table Mappings

The models map to the SQL Server tables in the 'cube' schema:

| Model Django     | SQL Server Table             |
|------------------|------------------------------|
| `DimDiseaseType` | `cube.DIM_DiseaseType`       |
| `DimDisease`     | `cube.DIM_Disease`           |
| `DimGene`        | `cube.DIM_Gene`              |
| `DimSource`      | `cube.DIM_Source`            |
| `DimVariant`     | `cube.DIM_Variant`           |
| `FactGda`        | `cube.FACT_GDA`              |
| `FactVda`        | `cube.FACT_VDA`              |

> Schema-qualified table names use the `[cube].[TABLE_NAME]` syntax in `db_table`, which produces the correct SQL Server square bracket notation.

## Project Structure

```
disgenet_project/
├── manage.py
├── requirements.txt
├── disgenet_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── disgenet_app/
    ├── models.py      ← cube tables mapping (managed=False)
    ├── views.py       ← about, search, stats + API JSON
    ├── urls.py        ← URL routes
    ├── static/
    │       └── img/
    └── templates/
        └── disgenet_app/
            ├── base.html             ← navigation + shared styles
            ├── about.html            ← About page
            ├── search.html           ← Search page
            ├── disease_detail.html   ← Disease Detail page
            └── stats.html            ← Statistics page
```
