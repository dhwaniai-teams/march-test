from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, text
import requests
import os

# Environment Variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DATABASE_URL = "postgresql://postgres:dhwaniai@localhost/dhwani_db"

# FastAPI app
app = FastAPI()

# Database Engine
engine = create_engine(DATABASE_URL)

class QueryRequest(BaseModel):
    question: str

# Fetch database schema
def get_db_schema():
    schema_query = """
    SELECT table_name, column_name, data_type 
    FROM information_schema.columns 
    WHERE table_schema = 'public'
    """
    with engine.connect() as conn:
        result = conn.execute(text(schema_query))
        schema = {}
        for row in result:
            table, column, dtype = row
            if table not in schema:
                schema[table] = []
            schema[table].append((column, dtype))
    return schema

# Generate SQL query dynamically using Groq API
def generate_sql_query(question, schema_info):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    schema_text = "\n".join(
        [f"Table: {table}, Columns: {', '.join([col for col, _ in cols])}" for table, cols in schema_info.items()]
    )

    prompt = f"""
    You are an AI that converts user questions into PostgreSQL queries. Given this schema:

    {schema_text}

    Convert the user's question into a **PostgreSQL SELECT query**. Only return the SQL query, nothing else.
    """

    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": question}
        ]
    }

    response = requests.post("https://api.groq.com/v1/chat/completions", headers=headers, json=data)
    response_data = response.json()
    sql_query = response_data["choices"][0]["message"]["content"].strip()

    if not sql_query.lower().startswith("select"):
        raise ValueError("Generated query is not a SELECT statement!")

    return sql_query

# Execute SQL query
def execute_query(query):
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return [dict(row) for row in result]

# Convert result to conversational text
def format_conversational_response(question, result):
    if not result:
        return "I'm sorry, but I couldn't find any relevant data in the database."
    
    response_text = f"Here’s what I found: "
    
    if isinstance(result, list) and isinstance(result[0], dict):
        rows = [', '.join(f"{key}: {value}" for key, value in row.items()) for row in result]
        response_text += ' | '.join(rows)
    else:
        response_text += str(result)
    
    return response_text

# API endpoint to query the database
@app.post("/query")
async def query_db(request: QueryRequest):
    try:
        schema_info = get_db_schema()
        sql_query = generate_sql_query(request.question, schema_info)
        result = execute_query(sql_query)
        conversational_response = format_conversational_response(request.question, result)
        return {"query": sql_query, "response": conversational_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
