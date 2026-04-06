import re
import json
from datetime import datetime

def _fix_trailing_commas(s: str) -> str:
    """Quita comas antes de } o ] (JSON inválido que a veces devuelve el modelo)."""
    s = re.sub(r",\s*}", "}", s)
    s = re.sub(r",\s*]", "]", s)
    return s


def _fix_missing_commas(s: str) -> str:
    """Añade comas entre propiedades de objeto cuando falta ( "value"\\n  "key": ).
    No añade si el " cierra un elemento de array ( ]\\n  "key" )."""
    def _repl(m: re.Match) -> str:
        prefix = s[: m.start()].rstrip()
        if prefix.endswith("]"):
            return m.group(0)
        
        return '"' + ',' + m.group(1) + '"' + m.group(2) + '":'
    s = re.sub(r'"(\s*\n\s*)"([a-zA-Z_][a-zA-Z0-9_]*)\s*":', _repl, s)
    return s


def _extract_json(text: str):
    """Intenta extraer un objeto JSON del texto (markdown, texto alrededor, comas finales)."""
    if not text or not text.strip():
        return None
    raw = text.strip()

    def try_parse(s: str, repair: bool = False):
        s = s.strip()
        s = _fix_missing_commas(s)
        s = _fix_trailing_commas(s)
        try:
            return json.loads(s)
        except json.JSONDecodeError:
            if not repair:
                return None
            
            for suffix in (
                "\"}",           # cortado dentro de un string (ej. creator_profile): cerrar " y }
                "\", \"target_audience\": \"\", \"content_style\": \"\"}",
                "\"]}",
                "]}", "]", "}",
            ):
                try:
                    return json.loads(_fix_trailing_commas(s + suffix))
                except json.JSONDecodeError:
                    continue
            return None


    out = try_parse(raw, repair=True)
    if out is not None:
        return out

    # 2) between ``` and ``` (complete answer)
    match = re.search(r"```\s*(?:json)?\s*\n?([\s\S]*?)\n?```", raw, re.IGNORECASE)
    if match:
        out = try_parse(match.group(1), repair=True)
        if out is not None:
            return out

    # 3) No closure
    if raw.startswith("```"):
        start = raw.find("{")
        if start != -1:
            out = try_parse(raw[start:], repair=True)
            if out is not None:
                return out

    # 4) between {} with closure
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        out = try_parse(raw[start : end + 1], repair=True)
        if out is not None:
            return out

    # 5) truncated ans without }: 
    if start != -1:
        out = try_parse(raw[start:], repair=True)
        if out is not None:
            return out
    return None


