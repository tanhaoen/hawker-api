import os
from dotenv import load_dotenv

load_dotenv()

DRIVER = '{ODBC Driver 18 for SQL Server}'

def get_pyodbc_connection_string():
    return f'DRIVER={DRIVER};SERVER=tcp:{os.environ["SERVER"]};PORT=1433;DATABASE={os.environ["DATABASE"]};UID={os.environ["USERNAME"]};PWD={{{os.environ["PASSWORD"]}}};'