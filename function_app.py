import azure.functions as func
import logging
import json
import pyodbc
from json import JSONEncoder
import datetime
from db_config import get_pyodbc_connection_string
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
import time

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

max_retries = 3

# subclass JSONEncoder
class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()

# Define a decorator with the retry configuration
@retry(
    stop=stop_after_attempt(max_retries),
    wait=wait_exponential(multiplier=1, max=10)
)
def connect_to_database():
    return pyodbc.connect(get_pyodbc_connection_string())

@app.function_name(name="getStalls")
@app.route(route="stalls")
def getStalls(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info('Python HTTP trigger function processed a request.')
        
        start_time = time.time()

        req_body = req.get_json()
        sort_by = req_body.get('sort_by','stall_name')
        sort_direction = 'desc' if req_body.get('desc',False) else 'asc'
        offset = req_body.get('offset',0)
        limit = req_body.get('limit', 10)
        limit = 30 if limit > 30 else limit
        
        query_str = f"""
        SELECT * FROM burpple_stall_overview
        ORDER BY {sort_by} {sort_direction}
        OFFSET {offset} ROWS
        FETCH NEXT {limit} ROWS ONLY;
        """
        
        conn_start_time = time.time()
        
        with connect_to_database() as conn:
            logging.info(f"Time taken to establish connection: {time.time() - conn_start_time} seconds")
            
            cursor = conn.cursor()
            
            query_start_time = time.time()
            
            cursor.execute(query_str)
            
            logging.info(f"Time taken to execute query: {time.time() - query_start_time} seconds")
            
            rows = []
            for row in cursor.fetchall():
                row_dict = dict(zip([column[0] for column in cursor.description], row))
                try:
                    row_dict['categories'] = json.loads(row_dict.get('categories', ''))
                except json.JSONDecodeError:
                    row_dict['categories'] = []
                rows.append(row_dict)
                
        response = {}
        
        response['num_results'] = len(rows)
        response['results'] = rows
        
        json_data = json.dumps(response, cls=DateTimeEncoder)
        
        logging.info(f"Time taken to process request: {time.time() - start_time} seconds")

        return func.HttpResponse(
            json_data,
            status_code=200,
            mimetype="application/json"
        )
    except RetryError as e:
        return func.HttpResponse(f"Error: Unable to establish a database connection after {max_retries} attempts.", status_code=500)
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)