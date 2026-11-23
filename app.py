import os
import psycopg
import logging
from fastapi import HTTPException
from fastapi import FastAPI  #for bringing fastapi class in my python program
from pydantic import BaseModel, Field, field_validator
from fastapi.responses import JSONResponse
app = FastAPI()

#Logging Config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

#Exception Handling 
@app.exception_handler(psycopg.Error)
async def database_exception_handler(request, exc): #async helps us handle multiple requests without blocking server
    #request captures incoming call details from http
    #exc captures the specific error

    #Logger's error
    logger.error(
                    "Database error on %s %s: %s",
                    request.method,
                    request.url.path,
                    exc
                )
    
    return JSONResponse(
        status_code=503,
        content={"detail": "Database Unavailable"}

    )


# Database connection
def get_db_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

# Health check

@app.get("/db-check")
def db_check():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
    return {"database": "Connected", "result": result[0]}

class User(BaseModel):
    name: str = Field(min_length=1, max_length=100)

    # Setting rules for input

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip() #Removes heading and trailing spaces

        if not value:
            raise ValueError("Name cannot be an empty space.")

        #all() ensures that atleast one condition is satisfied.
        if not all(char.isalpha() or char in " -'" for char in value):
            raise ValueError("Name contains invalid characters")

        return value


#Fastapi uses decorators
@app.post("/greet")
def greet_user(user:User):
    return {"message":f"Hello {user.name}, welcome to CloudOps project."}


@app.get("/") #endpoint 1
def get_home():
    return {
            "message":"CloudOps Application",
            "version":"1.0.0"
           }

@app.get("/health") #endpoint 2
def get_health():
    return {"status":"Healthy"}

@app.get("/version") #endpoint 3
def get_version():
    return {"version":"1.0.0"}

@app.post("/users")
def create_user(user: User):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (name) VALUES (%s) RETURNING id, name",
                (user.name,)
            )
            new_user = cur.fetchone()  #fetchone to fetch one value at a time(returns one row)
            logger.info("User Created Successfully. ID=%s", new_user[0]) 

    return {"id": new_user[0], "name": new_user[1]}


@app.get("/users") # To get the whole table
def get_users():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM users"
            )
            users = cur.fetchall() #fetchall to fetch whole table(returns all rows)
            logger.info("Successfully retrieved %s users", len(users))

    return[
        {"id": row[0], "name": row[1]}
        for row in users
    ] 

@app.get("/users/{user_id}")
def get_user(user_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM users WHERE id = %s",
                (user_id,)
            )
            user = cur.fetchone()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return {"id": user[0], "name": user[1]}

   
class UserUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=100)

    # Setting rules for input

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip() #Removes heading and trailing spaces

        if not value:
            raise ValueError("Name cannot be an empty space.")

        #all() ensures that atleast one condition is satisfied.
        if not all(char.isalpha() or char in " -'" for char in value):
            raise ValueError("Name contains invalid characters")

        return value


@app.put("/users/{user_id}")
def update_user(user_id: int, user: UserUpdate): 
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET name = %s WHERE id = %s RETURNING id, name",
                (user.name, user_id)
            )
            updated_user = cur.fetchone()
            

    if updated_user is None:
        logger.warning("User not found. ID=%s", user_id)
        raise HTTPException(status_code=404, detail="User not found.")
    logger.info("User updated successfully. ID=%s", updated_user[0])

    return {"id": updated_user[0], "name": updated_user[1]}

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM users WHERE id = %s RETURNING id, name",
                (user_id,)

            )
            deleted_user = cur.fetchone()
            

    if deleted_user is None:
        logger.warning("User not found. ID=%s", user_id)
        raise HTTPException(status_code=404, detail="User not found.")

    logger.info("User Deleted Successfully. ID=%s", deleted_user[0])

    return {
                "message": "User deleted successfully.",
                "user": {"id": deleted_user[0], "name": deleted_user[1]}

    }