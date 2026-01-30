"""
Brightdock Content Repurposer
A simple web app to discover AI research and generate blog drafts.
"""

import os
from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
from content_fetcher import ContentFetcher
from blog_generator import BlogGenerator
from database import Database

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize components
db = Database()
fetcher = ContentFetcher()
generator = BlogGenerator()


@app.route('/')
def index():
    """Render the main dashboard."""
    return render_template('index.html')


@app.route('/api/fetch', methods=['POST'])
def fetch_content():
    """Fetch new content from research sources."""
    try:
        articles = fetcher.fetch_all()
        for article in articles:
            db.save_article(article)
        return jsonify({
            'success': True,
            'count': len(articles),
            'message': f'Found {len(articles)} new articles'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/articles')
def get_articles():
    """Get all saved articles."""
    articles = db.get_articles()
    return jsonify(articles)


@app.route('/api/generate', methods=['POST'])
def generate_draft():
    """Generate a blog draft from an article."""
    data = request.json
    article_id = data.get('article_id')

    if not article_id:
        return jsonify({'success': False, 'error': 'Article ID required'}), 400

    article = db.get_article(article_id)
    if not article:
        return jsonify({'success': False, 'error': 'Article not found'}), 404

    try:
        draft = generator.generate(article)
        draft_id = db.save_draft(draft)
        draft['id'] = draft_id
        return jsonify({'success': True, 'draft': draft})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/drafts')
def get_drafts():
    """Get all saved drafts."""
    drafts = db.get_drafts()
    return jsonify(drafts)


@app.route('/api/drafts/<int:draft_id>')
def get_draft(draft_id):
    """Get a specific draft."""
    draft = db.get_draft(draft_id)
    if draft:
        return jsonify(draft)
    return jsonify({'error': 'Draft not found'}), 404


@app.route('/api/search', methods=['POST'])
def search_content():
    """Search for specific topics."""
    data = request.json
    query = data.get('query', '')

    if not query:
        return jsonify({'success': False, 'error': 'Query required'}), 400

    try:
        articles = fetcher.search(query)
        for article in articles:
            db.save_article(article)
        return jsonify({
            'success': True,
            'count': len(articles),
            'message': f'Found {len(articles)} articles for "{query}"'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
