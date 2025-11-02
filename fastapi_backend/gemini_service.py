import os
import json
import re

try:
    from google import genai
    from google.genai.types import GenerateContentConfig
    _HAS_GENAI = True
except Exception:
    _HAS_GENAI = False


class GeminiService:
    def __init__(self, api_key: str = None):
        self.client = None
        if _HAS_GENAI:
            api_key = api_key or os.environ.get("GEMINI_API_KEY")
            if api_key:
                try:
                    self.client = genai.Client(api_key=api_key)
                except Exception:
                    self.client = None

    def _extract_text(self, resp):
        """Extract text from Gemini response"""
        text = getattr(resp, "text", None)
        if not text:
            parts = []
            for cand in getattr(resp, "candidates", []) or []:
                content = getattr(cand, "content", None)
                if content and getattr(content, "parts", None):
                    for part in content.parts:
                        t = getattr(part, "text", None)
                        if t:
                            parts.append(t)
            text = "\n".join(parts).strip() if parts else ""
        return (text or "").strip()

    def _dedupe_and_clip(self, items):
        """Deduplicate and clip to 10 items"""
        out = []
        for x in items:
            x = x.strip()
            if len(x) < 4:
                continue
            if x.lower().startswith(("note:", "disclaimer:")):
                continue
            if not x.endswith("."):
                x += "."
            if x not in out:
                out.append(x)
        return out[:10]

    def _try_json(self, model_name: str, breed_name: str):
        """Try to get facts in JSON format"""
        sys_inst = (
            "Return ONLY valid JSON with this exact schema: "
            '{"facts": ["fact1", "fact2", "...", "fact10"]}. '
            "No prose, markdown, or backticks."
        )
        prompt = f"""
You are a camel-breed expert.
Provide exactly 10 distinct, single-sentence facts about '{breed_name}'.
Each fact ≤ 22 words. No numbering. No duplicates.
Output only JSON as instructed.
"""
        resp = self.client.models.generate_content(
            model=model_name,
            contents=f"{sys_inst}\n\n{prompt}",
            config=GenerateContentConfig(temperature=0.2, max_output_tokens=900),
        )
        text = self._extract_text(resp)
        if not text:
            return []
        try:
            data = json.loads(text)
        except Exception:
            m = re.search(r"\{.*\}", text, flags=re.S)
            if not m:
                return []
            try:
                data = json.loads(m.group(0))
            except Exception:
                return []
        facts = data.get("facts", []) if isinstance(data, dict) else []
        return self._dedupe_and_clip([str(x) for x in facts])

    def _try_bullets(self, model_name: str, breed_name: str):
        """Try to get facts in bullet format"""
        prompt = f"""
You are a camel-breed expert.
Write EXACTLY 10 distinct, single-sentence facts about '{breed_name}'.
Rules:
- Each fact MUST be on its own line starting with a single dash and a space: "- fact..."
- No numbering, no extra lines, no intro or outro text.
- Each fact ≤ 22 words.
Output ONLY those 10 bullet lines.
"""
        resp = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=GenerateContentConfig(temperature=0.3, max_output_tokens=900),
        )
        text = self._extract_text(resp)
        if not text:
            return []
        lines = [ln.strip()[2:].strip() for ln in text.splitlines() if ln.strip().startswith("- ")]
        return self._dedupe_and_clip(lines)

    def _try_plain(self, model_name: str, breed_name: str):
        """Try to get facts in plain newline format"""
        prompt = f"""
List EXACTLY 10 distinct, single-sentence facts about '{breed_name}'. No numbering.
Separate each fact by a newline. No extra text before or after.
Each fact ≤ 22 words.
"""
        resp = self.client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=GenerateContentConfig(temperature=0.35, max_output_tokens=900),
        )
        text = self._extract_text(resp)
        if not text:
            return []
        lines = [ln.strip() for ln in text.splitlines() if len(ln.strip()) > 3]
        facts = self._dedupe_and_clip(lines)
        if len(facts) >= 10:
            return facts
        rough = re.split(r"[.\n]+", text)
        rough = [r.strip() for r in rough if len(r.strip()) > 5]
        return self._dedupe_and_clip(rough)

    def get_10_facts(self, breed_name: str):
        """
        Get exactly 10 facts about a camel breed
        Returns: (facts_list, error_msg)
        """
        if self.client is None or not _HAS_GENAI:
            return [], "Gemini client not available or SDK not installed"

        strategies = [
            ("gemini-2.0-flash-exp", self._try_json),
            ("gemini-2.0-flash-exp", self._try_bullets),
            ("gemini-2.0-flash-exp", self._try_plain),
        ]

        last_err = None
        for model_name, fn in strategies:
            for attempt in range(2):  # Two attempts per strategy
                try:
                    facts = fn(model_name, breed_name)
                    if len(facts) == 10:
                        return facts, None
                    else:
                        last_err = f"Got {len(facts)} facts from {model_name} via {fn.__name__}."
                except Exception as e:
                    last_err = f"{type(e).__name__} on {model_name}/{fn.__name__}: {e}"

        return [], last_err or "Could not obtain 10 facts"


# Global service instance
_gemini_instance = None

def get_gemini_service():
    """Singleton pattern for Gemini service"""
    global _gemini_instance
    if _gemini_instance is None:
        _gemini_instance = GeminiService()
    return _gemini_instance
