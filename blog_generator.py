"""
Blog Generator Module
Uses Claude API to generate blog drafts from research papers.
"""

import os
import anthropic
from datetime import datetime


class BlogGenerator:
      """Generates blog drafts using Claude API."""

    SYSTEM_PROMPT = """You are a content writer for Brightdock, a company that teaches people how to create AI-generated images and videos. Your job is to transform technical research papers into engaging, accessible blog posts.

    ## Your Writing Style:
    - **Tone:** Educational but conversational, enthusiastic about AI possibilities
    - **Audience:** Creators, artists, and enthusiasts learning AI image/video tools
    - **Avoid:** Overly academic jargon, hype without substance, clickbait
    - **Include:** Practical examples, relatable analogies, actionable insights
    - **Perspective:** "We're exploring this together" — guide, not lecturer

    ## Important Guidelines:
    1. Make complex concepts accessible without dumbing them down
    2. Always connect research to practical applications for creators
    3. Use analogies that relate to art, photography, or video production
    4. Highlight what's genuinely exciting without overpromising
    5. Include specific, actionable takeaways readers can use"""

    BLOG_TEMPLATE = """Based on the following research paper, write a blog post for Brightdock's audience.

    ## Research Paper Details:
    **Title:** {title}
    **Authors:** {authors}
    **Source:** {source}
    **URL:** {url}

    **Abstract/Summary:**
    {summary}

    ---

    ## Your Task:
    Create a blog post (800-1200 words) with the following structure:

    # [Create an engaging title that would appeal to AI creators]

    **Meta Description:** [Write a 150-160 character SEO summary]

    **Target Keywords:** [List 3-5 relevant keywords]

    ---

    ## Introduction
    [Hook the reader — why this matters for AI creators. 2-3 paragraphs]

    ## What the Research Shows
    [Summarize the key findings in accessible language. 3-4 paragraphs]

    ## Practical Applications
    [How can Brightdock students/users apply this? 2-3 paragraphs]

    ## Key Takeaways
    - [Actionable insight 1]
    - [Actionable insight 2]
    - [Actionable insight 3]

    ## What's Next
    [Forward-looking conclusion. 1-2 paragraphs]

    ---

    **Source:** [{title}]({url})
    **Generated:** {date}

    Write the complete blog post now:"""

    def __init__(self):
              self.api_key = os.getenv('ANTHROPIC_API_KEY')
              if not self.api_key:
                            print("Warning: ANTHROPIC_API_KEY not found in environment variables")

          def generate(self, article):
                    """Generate a blog draft from an article."""
                    if not self.api_key:
                                  raise ValueError(
                                                    "ANTHROPIC_API_KEY not set. Please add your API key to the .env file.\n"
                                                    "Get your key from: https://console.anthropic.com/settings/keys"
                                  )

                    authors = article.get('authors', [])
                    if isinstance(authors, list):
                                  authors_str = ", ".join(authors[:5])
                                  if len(authors) > 5:
                                                    authors_str += " et al."
                    else:
                                  authors_str = str(authors)

                    prompt = self.BLOG_TEMPLATE.format(
                        title=article.get('title', 'Untitled'),
                        authors=authors_str,
                        source=article.get('source', 'Unknown'),
                        url=article.get('url', ''),
                        summary=article.get('summary', 'No summary available'),
                        date=datetime.now().strftime('%B %d, %Y')
                    )

        client = anthropic.Anthropic(api_key=self.api_key)

        message = client.messages.create(
                      model="claude-sonnet-4-20250514",
                      max_tokens=4096,
                      system=self.SYSTEM_PROMPT,
                      messages=[
                                        {"role": "user", "content": prompt}
                      ]
        )

        draft = message.content[0].text

        return {
                      'content': draft,
                      'source_title': article.get('title'),
                      'source_url': article.get('url'),
                      'generated_at': datetime.now().isoformat(),
                      'model': 'claude-sonnet-4-20250514',
                      'tokens_used': message.usage.input_tokens + message.usage.output_tokens
        }

    def test_connection(self):
              """Test the API connection."""
              if not self.api_key:
                            return False, "API key not configured"

              try:
                            client = anthropic.Anthropic(api_key=self.api_key)
                            message = client.messages.create(
                                model="claude-sonnet-4-20250514",
                                max_tokens=10,
                                messages=[{"role": "user", "content": "Hi"}]
                            )
                            return True, "Connection successful"
except anthropic.AuthenticationError:
            return False, "Invalid API key"
except Exception as e:
            return False, str(e)
