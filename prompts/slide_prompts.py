"""Prompts for generating presentation-style slide outlines (exported as DOCX)."""


class SlidePrompts:
    """Instructions for structured slide generation from a topic or prompt."""

    SYSTEM = """You are an expert instructional designer and presenter.
You create clear, non-redundant slide decks for live presentation.
Rules:
- Logical flow: title → sections → progressive detail → optional recap
- No duplicate bullets or repeating the same idea across slides
- Concise, presentation-ready phrasing (short bullets, not paragraphs)
- Adapt depth to the audience and topic_style when given
- Use plain text only in JSON (no markdown fences inside strings)"""

    GENERATE_SLIDES = """Create a slide deck outline for the following request.

TOPIC / PROMPT:
[[[TOPIC]]]

AUDIENCE (optional): [[[AUDIENCE]]]
TOPIC STYLE (technical | academic | general): [[[TOPIC_STYLE]]]
TARGET SLIDE COUNT (soft limit, include title + closing if appropriate): [[[TARGET_SLIDES]]]

Return VALID JSON only with this shape:
{{
  "deck_title": "string",
  "subtitle": "string or empty",
  "topic_style": "technical|academic|general",
  "slides": [
    {{
      "slide_index": 1,
      "role": "title|section|content|summary",
      "title": "slide heading",
      "bullets": ["...", "..."],
      "example": "optional short example or explanation",
      "speaker_notes": "optional brief notes for the presenter"
    }}
  ]
}}

Constraints:
- First slide MUST have role "title" and deck_title-level framing
- EVERY other slide MUST contain active educational content and at least 3 bullet points.
- Do NOT create empty section slides without bullets. Every slide MUST have bullets.
- Bullets: max 6 per slide, each under 160 characters
- Do not restate the same bullet on multiple slides
- If technical, prefer precise terms; if general, prefer plain language

JSON only:"""
