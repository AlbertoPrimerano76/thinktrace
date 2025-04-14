import json
import re
from core import logger 


def clean_nulls_in_json_string(json_str: str) -> str:
    # Replace `"key": null` with `"key": ""` where key is known
    cleaned = re.sub(r'"description"\s*:\s*null', '"description": ""', json_str)
    cleaned = re.sub(r'"final_output_format"\s*:\s*null', '"final_output_format": ""', cleaned)
    cleaned = re.sub(r'"intent"\s*:\s*null', '"intent": ""', cleaned)
    return cleaned



# 🔎 Extract JSON from model response
def extract_json_from_response(content: str, strict: bool = False) -> dict:
    lines = content.strip().splitlines()
    if lines and lines[0].strip().lower() == "json":
        content = "\n".join(lines[1:])

    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
    if match:
        content = match.group(1).strip()
        logger.debug("🧩 Found JSON block inside backticks.")
    else:
        logger.warning("⚠️ No ```json``` block found — trying full content as raw JSON.")

    try:
        data = json.loads(content)
        content = clean_nulls_in_json_string(content)
        for step in data.get("reasoning_steps", []):
            if "infferred_facts" in step:
                step["inferred_facts"] = step.pop("infferred_facts")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse JSON: {e} --- Raw content start --- {content}--- end ---")
        if strict:
            raise
        return {}
