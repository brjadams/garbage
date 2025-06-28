import psycopg2
import numpy as np

# Connect to the database
user = "myuser"
db = "mydatabase"

conn = psycopg2.connect(
    dbname="mydatabase", user="myuser", password="mypassword", host="localhost"
)
cur = conn.cursor()

cur.execute(
    """
    CREATE TABLE IF NOT EXISTS documents (
        id SERIAL PRIMARY KEY,
        content TEXT,
        embedding vector(1536)
    )
"""
)
# Insert a vector
embedding = np.array([1.5, 2.5, 3.5])
cur.execute("""
            INSERT INTO items (embedding) VALUES (%s)
            """, (embedding.tolist(),))

# Perform a similarity search
query_vector = np.array([2, 3, 4])
cur.execute(
    """
    SELECT * FROM items ORDER BY embedding <-> %s LIMIT 1
    """, (str(query_vector.tolist()),))
result = cur.fetchone()
print(f"Nearest neighbor: {result}")

conn.commit()
cur.close()
conn.close()
