import sqlite3
from typing import List, Optional
from models import Meme, Tag


class DatabaseConnection:
    _instance = None

    def __new__(cls, db_path="memes.db"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.connection = sqlite3.connect(db_path)
            cls._instance.connection.row_factory = sqlite3.Row
            cls._instance._create_tables()
        return cls._instance

    def _create_tables(self):
        cursor = self.connection.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS memes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                image_path TEXT NOT NULL,
                date_added DATETIME DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT
            );
            CREATE TABLE IF NOT EXISTS meme_tags (
                meme_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                PRIMARY KEY (meme_id, tag_id),
                FOREIGN KEY (meme_id) REFERENCES memes(id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
            );
        """)
        self.connection.commit()

    def get_cursor(self):
        return self.connection.cursor()

    def commit(self):
        self.connection.commit()


class MemeRepository:
    def __init__(self):
        self.db = DatabaseConnection()

    def add_meme(self, meme):
        cursor = self.db.get_cursor()
        cursor.execute(
            "INSERT INTO memes (title, description, image_path) VALUES (?, ?, ?)",
            (meme.title, meme.description, meme.image_path)
        )
        meme_id = cursor.lastrowid
        for tag in meme.tags:
            tag_id = self._get_or_create_tag(tag.name, tag.description)
            cursor.execute(
                "INSERT OR IGNORE INTO meme_tags (meme_id, tag_id) VALUES (?, ?)",
                (meme_id, tag_id)
            )
        self.db.commit()
        return meme_id

    def _get_or_create_tag(self, name, description=None):
        cursor = self.db.get_cursor()
        cursor.execute("SELECT id FROM tags WHERE name = ?", (name,))
        row = cursor.fetchone()
        if row:
            return row["id"]
        cursor.execute(
            "INSERT INTO tags (name, description) VALUES (?, ?)",
            (name, description)
        )
        return cursor.lastrowid

    def get_all_memes(self):
        cursor = self.db.get_cursor()
        cursor.execute("SELECT * FROM memes ORDER BY date_added DESC")
        rows = cursor.fetchall()
        return [self._row_to_meme(row) for row in rows]

    def _row_to_meme(self, row):
        meme = Meme(
            id=row["id"],
            title=row["title"],
            description=row["description"] or "",
            image_path=row["image_path"],
            date_added=row["date_added"],
        )
        meme.tags = self.get_tags_for_meme(meme.id)
        return meme

    def get_tags_for_meme(self, meme_id):
        cursor = self.db.get_cursor()
        cursor.execute(
            "SELECT t.id, t.name, t.description FROM tags t "
            "JOIN meme_tags mt ON t.id = mt.tag_id WHERE mt.meme_id = ?",
            (meme_id,)
        )
        return [Tag(id=r["id"], name=r["name"], description=r["description"])
                for r in cursor.fetchall()]

    def get_all_tags(self):
        cursor = self.db.get_cursor()
        cursor.execute("SELECT * FROM tags ORDER BY name")
        return [Tag(id=r["id"], name=r["name"], description=r["description"])
                for r in cursor.fetchall()]

    def delete_meme(self, meme_id):
        cursor = self.db.get_cursor()
        cursor.execute("DELETE FROM memes WHERE id = ?", (meme_id,))
        self.db.commit()

    def update_meme(self, meme):
        cursor = self.db.get_cursor()
        cursor.execute(
            "UPDATE memes SET title = ?, description = ? WHERE id = ?",
            (meme.title, meme.description, meme.id)
        )
        cursor.execute("DELETE FROM meme_tags WHERE meme_id = ?", (meme.id,))
        for tag in meme.tags:
            tag_id = self._get_or_create_tag(tag.name)
            cursor.execute(
                "INSERT OR IGNORE INTO meme_tags (meme_id, tag_id) VALUES (?, ?)",
                (meme.id, tag_id)
            )
        self.db.commit()

    def search_memes(self, text="", tag_ids=None, date_from=None, date_to=None):
        cursor = self.db.get_cursor()
        query = "SELECT DISTINCT m.* FROM memes m"
        conditions = []
        params = []

        if tag_ids:
            query += (
                " JOIN meme_tags mt ON m.id = mt.meme_id"
                " JOIN tags t ON mt.tag_id = t.id"
            )
            placeholders = ",".join("?" for _ in tag_ids)
            conditions.append("t.id IN (" + placeholders + ")")
            params.extend(tag_ids)

        if text:
            conditions.append("(m.title LIKE ? OR m.description LIKE ?)")
            params.extend(["%" + text + "%", "%" + text + "%"])

        if date_from:
            conditions.append("DATE(m.date_added) >= DATE(?)")
            params.append(date_from)

        if date_to:
            conditions.append("DATE(m.date_added) <= DATE(?)")
            params.append(date_to)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        if tag_ids:
            query += " GROUP BY m.id HAVING COUNT(DISTINCT t.id) = " + str(len(tag_ids))

        query += " ORDER BY m.date_added DESC"
        cursor.execute(query, params)
        return [self._row_to_meme(row) for row in cursor.fetchall()]

    def get_tag_usage_counts(self):
        cursor = self.db.get_cursor()
        cursor.execute(
            "SELECT t.name, COUNT(mt.meme_id) as cnt FROM tags t "
            "LEFT JOIN meme_tags mt ON t.id = mt.tag_id "
            "GROUP BY t.id ORDER BY cnt DESC"
        )
        return {row["name"]: row["cnt"] for row in cursor.fetchall()}
