"""Generate structured slide outlines from a topic using the text LLM."""
import json
from typing import Any, Dict, Optional

from llm_models.llm_models import llm
from prompts.slide_prompts import SlidePrompts
from utils.logger import log_error, log_step, log_success


class SlideService:
    """Produce slide deck JSON suitable for DOCX export or API consumption."""

    def _parse_json(self, response: str) -> Dict[str, Any]:
        text = response.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            log_error("Slide JSON parse failed", e)
            return {"error": str(e), "raw": text.strip()}

    def generate_slides(
        self,
        topic: str,
        audience: Optional[str] = None,
        topic_style: str = "general",
        target_slides: int = 10,
    ) -> Dict[str, Any]:
        log_step("Slide generation", f"style={topic_style}, target={target_slides}")
        allowed_styles = {"technical", "academic", "general"}
        ts = (topic_style or "general").strip().lower()
        if ts not in allowed_styles:
            ts = "general"
        topic_style = ts
        audience = audience or "Not specified"
        prompt = SlidePrompts.GENERATE_SLIDES.format(
            topic=topic.strip(),
            audience=audience,
            topic_style=topic_style,
            target_slides=max(3, min(target_slides, 40)),
        )
        messages = [
            {"role": "system", "content": SlidePrompts.SYSTEM},
            {"role": "user", "content": prompt},
        ]
        response = llm.invoke(messages)
        data = self._parse_json(response.content)
        if "error" in data and "slides" not in data:
            return {"success": False, "error": data.get("error", "Invalid JSON from model")}
        slides = data.get("slides") or []
        if not isinstance(slides, list):
            return {"success": False, "error": "Model returned invalid slides array"}
        log_success(f"Generated {len(slides)} slides")
        return {
            "success": True,
            "deck_title": data.get("deck_title", topic[:120]),
            "subtitle": data.get("subtitle", ""),
            "topic_style": data.get("topic_style", topic_style),
            "slides": slides,
        }
