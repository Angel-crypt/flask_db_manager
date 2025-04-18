import csv
import os
import random
import mysql.connector
from datetime import datetime

DB_NAME = 'filmHUB_db'
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '12345',
    'database': DB_NAME,
    'port': 3360
}

sample_tags = [
    "inspiring", "dark", "adventure", "based on true story", "cult classic", "emotional",
    "fast-paced", "thrilling", "dramatic", "family-friendly", "action-packed", "comedy",
    "sci-fi", "fantasy", "romantic", "mystery", "historical", "crime", "horror", "feel-good"
]


def connect_db():
    return mysql.connector.connect(**db_config)


def get_or_create(cursor, table, unique_column, value):
    cursor.execute(
        f"SELECT id FROM {table} WHERE {unique_column} = %s", (value,))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute(
        f"INSERT INTO {table} ({unique_column}) VALUES (%s)", (value,))
    return cursor.lastrowid


def get_or_create_director(cursor, name, surname):
    cursor.execute(
        "SELECT id FROM director WHERE name = %s AND surname = %s", (name, surname))
    result = cursor.fetchone()
    if result:
        return result[0]
    cursor.execute(
        "INSERT INTO director (name, surname) VALUES (%s, %s)", (name, surname))
    return cursor.lastrowid


def convert_duration_to_time(duration_str):
    try:
        # Eliminar "0 days" si está presente y extraer la parte del tiempo
        time_str = duration_str.split(" ")[-1]
        # Convertir la cadena de tiempo a un objeto datetime.time
        time_obj = datetime.strptime(time_str, '%H:%M:%S').time()
        return time_obj
    except Exception as e:
        print(f"Error al convertir duración: {e}")
        return None


def insert_content(cursor, row):
    # Convertir la duración al formato adecuado, con un valor por defecto si es None
    duration = convert_duration_to_time(row.get('duration', '0 days 00:00:00'))

    cursor.execute("""
        INSERT INTO content (title, classification, release_date, duration, summary, url_image, status, price, type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        row['title'],
        row.get('rated', 'NR'),
        row.get('release_date') or None,
        duration,
        row.get('summary') or '',
        row.get('url_image') or '',
        random.choice(['available', 'unavailable']),
        round(random.uniform(10.0, 100.0), 2),
        row.get('type') or 'movie'
    ))
    return cursor.lastrowid


CSV_FILE_PATH = os.path.join(os.path.dirname(
    __file__), 'movies_data_clean.csv')


def main():
    conn = connect_db()
    cursor = conn.cursor()

    with open(CSV_FILE_PATH, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                content_id = insert_content(cursor, row)

                # Director
                if row['director']:
                    parts = row['director'].split()
                    name = parts[0]
                    surname = ' '.join(parts[1:]) if len(parts) > 1 else ''
                    director_id = get_or_create_director(cursor, name, surname)
                    cursor.execute(
                        "INSERT INTO content_director (content_id, director_id) VALUES (%s, %s)", (content_id, director_id))

                # Genre
                if row['genre']:
                    genres = [g.strip() for g in row['genre'].split(',')]
                    for genre in genres:
                        genre_id = get_or_create(
                            cursor, 'genre', 'name', genre)
                        cursor.execute(
                            "INSERT INTO content_genre (genre_id, content_id) VALUES (%s, %s)", (genre_id, content_id))

                # Tags (auto-generated)
                tags = random.sample(sample_tags, k=2)
                for tag in tags:
                    tag_id = get_or_create(cursor, 'tag', 'name', tag)
                    cursor.execute(
                        "INSERT INTO content_tag (tag_id, content_id) VALUES (%s, %s)", (tag_id, content_id))

                print(f"Inserted: {row['title']}")
            except Exception as e:
                print(f"Error inserting {row['title']}: {e}")
                conn.rollback()
                continue

            conn.commit()

    cursor.close()
    conn.close()


if __name__ == '__main__':
    main()