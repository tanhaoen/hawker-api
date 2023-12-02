import azure.functions as func
import logging
import json
import pyodbc
from json import JSONEncoder
import datetime
from db_config import get_pyodbc_connection_string

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

# subclass JSONEncoder
class DateTimeEncoder(JSONEncoder):
        #Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()

@app.function_name(name="getStalls")
@app.route(route="stalls")
def getStalls(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info('Python HTTP trigger function processed a request.')

        req_body = req.get_json()
        sort_by = req_body.get('sort_by','stall_name')
        sort_direction = 'desc' if req_body.get('desc',False) else 'asc'
        offset = req_body.get('offset',0)
        limit = req_body.get('limit', 10)
        
        query_str = f"""
        SELECT * FROM burpple_stall_overview
        ORDER BY {sort_by} {sort_direction}
        OFFSET {offset} ROWS
        FETCH NEXT {limit} ROWS ONLY;
        """
        
        with pyodbc.connect(get_pyodbc_connection_string()) as conn:
            cursor = conn.cursor()
            cursor.execute(query_str)
            rows = []
            for row in cursor.fetchall():
                row_dict = dict(zip([column[0] for column in cursor.description], row))
                try:
                    row_dict['categories'] = json.loads(row_dict.get('categories', ''))
                except json.JSONDecodeError:
                    row_dict['categories'] = []
                rows.append(row_dict)
        
        json_data = json.dumps(rows, cls=DateTimeEncoder)

        return func.HttpResponse(
            json_data,
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)