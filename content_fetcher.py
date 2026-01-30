"""
Content Fetcher Module
Fetches AI research papers and articles from various sources.
"""

import arxiv
import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import hashlib


class ContentFetcher:
      """Fetches content from research sources."""

    DEFAULT_TOPICS = [
              "diffusion models image generation",
              "text to image generation",
              "video synthesis deep learning",
              "LoRA fine-tuning",
              "stable diffusion training",
              "generative adversarial networks images",
              "neural network image editing",
              "AI video generation",
    ]

    def __init__(self):
              self.arxiv_client = arxiv.Client()

    def fetch_all(self, max_results=20):
              """Fetch from all sources."""
              articles = []
              arxiv_articles = self.fetch_arxiv(max_results=max_results)
              articles.extend(arxiv_articles)
              hf_articles = self.fetch_huggingface_papers(max_results=5)
              articles.extend(hf_articles)
              return articles

    def fetch_arxiv(self, query=None, max_results=15):
              """Fetch papers from ArXiv."""
              if query is None:
                            query = " OR ".join([f'"{topic}"' for topic in self.DEFAULT_TOPICS[:4]])

              search = arxiv.Search(
                  query=f"cat:cs.CV AND ({query})",
                  max_results=max_results,
                  sort_by=arxiv.SortCriterion.SubmittedDate,
                  sort_order=arxiv.SortOrder.Descending
              )

        articles = []
        try:
                      for paper in self.arxiv_client.results(search):
                                        article = {
                                                              'id': self._generate_id(paper.entry_id),
                                                              'title': paper.title,
                                                              'summary': paper.summary,
                                                              'authors': [author.name for author in paper.authors[:5]],
                                                              'url': paper.entry_id,
                                                              'pdf_url': paper.pdf_url,
                                                              'published': paper.published.isoformat() if paper.published else None,
                                                              'source': 'arxiv',
                                                              'categories': paper.categories,
                                                              'fetched_at': datetime.now().isoformat()
                                        }
                                        articles.append(article)
        except Exception as e:
                      print(f"Error fetching from ArXiv: {e}")
                  return articles

    def fetch_huggingface_papers(self, max_results=5):
              """Fetch papers from Hugging Face daily papers."""
              articles = []
              try:
                            response = requests.get("https://huggingface.co/api/daily_papers", timeout=10)
                            if response.status_code == 200:
                                              papers = response.json()[:max_results]
                                              for paper in papers:
                                                                    article = {
                                                                                              'id': self._generate_id(paper.get('paper', {}).get('id', '')),
                                                                                              'title': paper.get('paper', {}).get('title', 'Untitled'),
                                                                                              'summary': paper.get('paper', {}).get('summary', ''),
                                                                                              'authors': paper.get('paper', {}).get('authors', [])[:5],
                                                                                              'url': f"https://huggingface.co/papers/{paper.get('paper', {}).get('id', '')}",
                                                                                              'pdf_url': None,
                                                                                              'published': paper.get('publishedAt', None),
                                                                                              'source': 'huggingface',
                                                                                              'categories': [],
                                                                                              'fetched_at': datetime.now().isoformat()
                                                                    }
                                                                    if article['title'] != 'Untitled':
                                                                                              articles.append(article)
              except Exception as e:
                            print(f"Error fetching from Hugging Face: {e}")
                        return articles

    def search(self, query, max_results=10):
              """Search for specific topics."""
        return self.fetch_arxiv(query=query, max_results=max_results)

    def _generate_id(self, url):
              """Generate a unique ID from URL."""
        return hashlib.md5(url.encode()).hexdigest()[:12]
