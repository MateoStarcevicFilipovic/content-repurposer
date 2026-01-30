/**
 * Brightdock Content Repurposer - Frontend
 */

let articles = [];
let drafts = [];
let selectedArticle = null;
let currentDraft = null;

const fetchBtn = document.getElementById('fetchBtn');
const searchBtn = document.getElementById('searchBtn');
const searchInput = document.getElementById('searchInput');
const articlesList = document.getElementById('articlesList');
const articlePreview = document.getElementById('articlePreview');
const draftsList = document.getElementById('draftsList');
const draftModal = document.getElementById('draftModal');
const draftContent = document.getElementById('draftContent');

document.addEventListener('DOMContentLoaded', () => {
      loadArticles();
      loadDrafts();
      setupEventListeners();
});

function setupEventListeners() {
      fetchBtn.addEventListener('click', fetchNewContent);
      searchBtn.addEventListener('click', searchContent);
      searchInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') searchContent();
      });
      document.querySelectorAll('.tab').forEach(tab => {
                tab.addEventListener('click', () => switchTab(tab.dataset.tab));
      });
}

function switchTab(tabName) {
      document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      document.querySelector(`.tab[data-tab="${tabName}"]`).classList.add('active');
      document.getElementById(tabName).classList.add('active');
}

async function fetchNewContent() {
      setLoading(fetchBtn, true);
      try {
                const response = await fetch('/api/fetch', { method: 'POST' });
                const data = await response.json();
                if (data.success) {
                              showToast(`Found ${data.count} new papers!`, 'success');
                              loadArticles();
                } else {
                              showToast(data.error || 'Failed to fetch', 'error');
                }
      } catch (error) {
                showToast('Network error', 'error');
      }
      setLoading(fetchBtn, false);
}

async function searchContent() {
      const query = searchInput.value.trim();
      if (!query) return;
      setLoading(searchBtn, true);
      try {
                const response = await fetch('/api/search', {
                              method: 'POST',
                              headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({ query })
                });
                const data = await response.json();
                if (data.success) {
                              showToast(`Found ${data.count} papers`, 'success');
                              loadArticles();
                } else {
                              showToast(data.error || 'Search failed', 'error');
                }
      } catch (error) {
                showToast('Network error', 'error');
      }
      setLoading(searchBtn, false);
}

async function loadArticles() {
      try {
                const response = await fetch('/api/articles');
                articles = await response.json();
                renderArticles();
      } catch (error) {
                console.error('Failed to load articles:', error);
      }
}

function renderArticles() {
      if (articles.length === 0) {
                articlesList.innerHTML = '<p class="placeholder">Click "Fetch New" to discover papers</p>';
                return;
      }
      articlesList.innerHTML = articles.map(article => `
              <div class="article-card ${selectedArticle?.id === article.id ? 'active' : ''}"
                           onclick="selectArticle('${article.id}')">
                                       <h3>${escapeHtml(article.title)}</h3>
                                                   <div class="article-meta">
                                                                   <span class="article-source">${article.source}</span>
                                                                                   <span>${formatDate(article.published)}</span>
                                                                                               </div>
                                                                                                       </div>
                                                                                                           `).join('');
}

function selectArticle(articleId) {
      selectedArticle = articles.find(a => a.id === articleId);
      renderArticles();
      renderPreview();
}

function renderPreview() {
      if (!selectedArticle) {
                articlePreview.innerHTML = '<div class="placeholder"><h3>Select a paper</h3></div>';
                return;
      }
      const authors = Array.isArray(selectedArticle.authors) ? selectedArticle.authors.join(', ') : selectedArticle.authors;
      articlePreview.innerHTML = `
              <h2>${escapeHtml(selectedArticle.title)}</h2>
                      <div class="meta">
                                  <span><strong>Authors:</strong> ${escapeHtml(authors)}</span>
                                              <span><strong>Source:</strong> ${selectedArticle.source}</span>
                                                      </div>
                                                              <div class="summary"><p>${escapeHtml(selectedArticle.summary)}</p></div>
                                                                      <div class="actions">
                                                                                  <button class="btn btn-primary" onclick="generateDraft('${selectedArticle.id}')">Generate Draft</button>
                                                                                              <a href="${selectedArticle.url}" target="_blank" class="btn btn-secondary">View Original</a>
                                                                                                      </div>
                                                                                                          `;
}

async function generateDraft(articleId) {
      const btn = document.querySelector('.article-preview .btn-primary');
      btn.textContent = 'Generating...';
      btn.disabled = true;
      try {
                const response = await fetch('/api/generate', {
                              method: 'POST',
                              headers: { 'Content-Type': 'application/json' },
                              body: JSON.stringify({ article_id: articleId })
                });
                const data = await response.json();
                if (data.success) {
                              currentDraft = data.draft;
                              showDraftModal(data.draft);
                              loadDrafts();
                              showToast('Draft generated!', 'success');
                } else {
                              showToast(data.error || 'Generation failed', 'error');
                }
      } catch (error) {
                showToast('Network error', 'error');
      }
      btn.textContent = 'Generate Draft';
      btn.disabled = false;
}

async function loadDrafts() {
      try {
                const response = await fetch('/api/drafts');
                drafts = await response.json();
                renderDrafts();
      } catch (error) {
                console.error('Failed to load drafts:', error);
      }
}

function renderDrafts() {
      if (drafts.length === 0) {
                draftsList.innerHTML = '<p class="placeholder">No drafts yet</p>';
                return;
      }
      draftsList.innerHTML = drafts.map(draft => `
              <div class="draft-card">
                          <h3>${escapeHtml(draft.source_title || 'Untitled')}</h3>
                                      <div class="meta">Generated ${formatDate(draft.generated_at)}</div>
                                                  <button class="btn btn-primary btn-small" onclick="viewDraft(${draft.id})">View</button>
                                                          </div>
                                                              `).join('');
}

async function viewDraft(draftId) {
      try {
                const response = await fetch(`/api/drafts/${draftId}`);
                const draft = await response.json();
                currentDraft = draft;
                showDraftModal(draft);
      } catch (error) {
                showToast('Failed to load draft', 'error');
      }
}

function showDraftModal(draft) {
      draftContent.textContent = draft.content;
      draftModal.style.display = 'flex';
}

function closeModal() {
      draftModal.style.display = 'none';
}

function copyDraft() {
      if (!currentDraft) return;
      navigator.clipboard.writeText(currentDraft.content);
      showToast('Copied!', 'success');
}

function downloadDraft() {
      if (!currentDraft) return;
      const blob = new Blob([currentDraft.content], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `draft-${Date.now()}.md`;
      a.click();
      URL.revokeObjectURL(url);
}

draftModal.addEventListener('click', (e) => {
      if (e.target === draftModal) closeModal();
});

function setLoading(btn, loading) {
      const text = btn.querySelector('.btn-text');
      const loader = btn.querySelector('.btn-loading');
      if (text && loader) {
                text.style.display = loading ? 'none' : 'inline';
                loader.style.display = loading ? 'inline' : 'none';
      }
      btn.disabled = loading;
}

function showToast(message, type = 'info') {
      const toast = document.createElement('div');
      toast.className = `toast ${type}`;
      toast.textContent = message;
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3000);
}

function formatDate(dateString) {
      if (!dateString) return 'Unknown';
      try {
                return new Date(dateString).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
      } catch { return dateString; }
}

function escapeHtml(text) {
      if (!text) return '';
      const div = document.createElement('div');
      div.textContent = text;
      return div.innerHTML;
}
