from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

#  DATABASE CONNECTION
def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root1234",
        database="crime_db1"
    )

@app.route('/')
def home():
    return {"message": "CRMS Backend Running"}

# GET CRIMES
@app.route('/get_crimes', methods=['GET'])
def get_crimes():
    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        sort_by = request.args.get('sort_by', 'id')
        order = request.args.get('order', 'asc')
        date = request.args.get('date')

        if sort_by not in ['id', 'date', 'type', 'location']:
            sort_by = 'id'
        if order not in ['asc', 'desc']:
            order = 'asc'

        query = "SELECT * FROM crimes"
        params = []

        if date:
            query += " WHERE DATE(date) = %s"
            params.append(date)

        query += f" ORDER BY {sort_by} {order}"

        cursor.execute(query, tuple(params))
        data = cursor.fetchall()

        conn.close()
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})

# ADD CRIME
@app.route('/add_crime', methods=['POST'])
def add_crime():
    try:
        data = request.json
        conn = get_conn()
        cursor = conn.cursor()

        query = "INSERT INTO crimes (type, location, date, status) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (
            data['type'],
            data['location'],
            data['date'][:10],
            data.get('status', 'Open')
        ))

        conn.commit()
        conn.close()

        return jsonify({"message": "Crime added successfully"})

    except Exception as e:
        return jsonify({"error": str(e)})

# UPDATE CRIME
@app.route('/update_crime/<int:id>', methods=['PUT'])
def update_crime(id):
    try:
        data = request.json
        conn = get_conn()
        cursor = conn.cursor()

        query = """
        UPDATE crimes
        SET type=%s, location=%s, date=%s, status=%s
        WHERE id=%s
        """

        cursor.execute(query, (
            data['type'],
            data['location'],
            data['date'][:10],
            data['status'],
            id
        ))

        conn.commit()
        conn.close()

        return jsonify({"message": "Crime updated"})

    except Exception as e:
        return jsonify({"error": str(e)})

# DELETE CRIME
@app.route('/delete_crime/<int:id>', methods=['DELETE'])
def delete_crime(id):
    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM crimes WHERE id=%s", (id,))
        conn.commit()
        conn.close()

        return jsonify({"message": "Crime deleted"})

    except Exception as e:
        return jsonify({"error": str(e)})

# ===========================
# SEARCH
# ===========================
@app.route('/search_crime', methods=['GET'])
def search_crime():
    try:
        keyword = request.args.get('q', '')

        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM crimes WHERE type LIKE %s",
            ('%' + keyword + '%',)
        )

        data = cursor.fetchall()
        conn.close()

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})

# STATS 
@app.route('/crime_stats', methods=['GET'])
def crime_stats():
    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
        SELECT 
            COUNT(*) as total,
            MIN(date) as oldest,
            MAX(date) as latest
        FROM crimes
        """)

        data = cursor.fetchone()
        conn.close()

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})
# ===========================
# CRIME COUNT
# ===========================
@app.route('/crime_count', methods=['GET'])
def crime_count():
    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM crimes")
        count = cursor.fetchone()[0]

        conn.close()

        return jsonify({"count": count})

    except Exception as e:
        return jsonify({"error": str(e)})

# RECENT CRIMES
@app.route('/recent_crimes')
def recent_crimes():
    try:
        conn = get_conn()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
        SELECT * FROM crimes
        WHERE date >= CURDATE() - INTERVAL 7 DAY
        ORDER BY date DESC
        """)

        data = cursor.fetchall()
        conn.close()

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})

# RUN SERVER (IMPORTANT FOR NGROK)
if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
