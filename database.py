"""
Database Module
Simple SQLite database for storing articles and drafts.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path


class Database:
      """Simple SQLite database for the content repurposer."""

    def __init__(self, db_path='data/content.db'):
              self.db_path = db_path
              Path('data').mkdir(exist_ok=True)

    def _get_connection(self):
              conn = sqlite3.connect(self.db_path)
              conn.row_factory = sqlite3.Row
              return conn

    def init(self):
              """Initialize database tables."""
              conn = self._get_connection()
              cursor = conn.cursor()
              cursor.execute('''
                  CREATE TABLE IF NOT EXISTS articles (
                      id TEXT PRIMARY KEY, title TEXT NOT NULL, summary TEXT,
                      authors TEXT, url TEXT, pdf_url TEXT, published TEXT,
                      source TEXT, categories TEXT, fetched_at TEXT, relevance_score REAL DEFAULT 0
                  )
              ''')
              cursor.execute('''
                  CREATE TABLE IF NOT EXISTS drafts (
                      id INTEGER PRIMARY KEY AUTOINCREMENT, article_id TEXT,
                      content TEXT NOT NULL, source_title TEXT, source_url TEXT,
                      generated_at TEXT, model TEXT, tokens_used INTEGER,
                      FOREIGN KEY (article_id) REFERENCES articles(id)
                  )
              ''')
              conn.commit()
              conn.close()
              print("Database initialized successfully")

    def save_article(self, article):
              conn = self._get_connection()
              cursor = conn.cursor()
              authors = json.dumps(article.get('authors', []))
              categories = json.dumps(article.get('categories', []))
              cursor.execute('''
                  INSERT OR REPLACE INTO articles
                  (id, title, summary, authors, url, pdf_url, published, source, categories, fetched_at)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
              ''', (article['id'], article['title'], article.get('summary', ''), authors,
                    article.get('url', ''), article.get('pdf_url', ''), article.get('published', ''),
                    article.get('source', ''), categories, article.get('fetched_at', datetime.now().isoformat())))
              conn.commit()
              conn.close()
              return article['id']

    def get_articles(self, limit=50):
              conn = self._get_connection()
              cursor = conn.cursor()
              cursor.execute('SELECT * FROM articles ORDER BY fetched_at DESC LIMIT ?', (limit,))
              rows = cursor.fetchall()
              conn.close()
              articles = []
              for row in rows:
                            article = dict(row)
                            article['authors'] = json.loads(article['authors']) if article['authors'] else []
                            article['categories'] = json.loads(article['categories']) if article['categories'] else []
                            articles.append(article)
                        return articles

    def get_article(self, article_id):
              conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM articles WHERE id = ?', (article_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
                      article = dict(row)
                      article['authors'] = json.loads(article['authors']) if article['authors'] else []
                      article['categories'] = json.loads(article['categories']) if article['categories'] else []
                      return article
                  return None

    def save_draft(self, article_id, draft):
              conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
                    INSERT INTO drafts (article_id, content, source_title, source_url, generated_at, model, tokens_used)
                                VALUES (?, ?, ?, ?, ?, ?, ?)
                                        ''', (article_id, draft['content'], draft.get('source_title', ''), draft.get('source_url', ''),
                                                            draft.get('generated_at', datetime.now().isoformat()), draft.get('model', ''), draft.get('tokens_used', 0)))
        draft_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return draft_id

    def get_drafts(self, limit=20):
              conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM drafts ORDER BY generated_at DESC LIMIT ?', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_draft(self, draft_id):
              conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM drafts WHERE id = ?', (draft_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None
