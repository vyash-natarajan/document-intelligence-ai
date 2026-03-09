import re


def clean_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_sentences(text: str):
    if not text:
        return []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def generate_fallback_summary(document_type: str, text: str, structured_data: dict) -> dict:
    cleaned = clean_text(text)
    sentences = split_sentences(cleaned)

    short_summary = "No summary available."
    if sentences:
        short_summary = " ".join(sentences[:3])[:700]

    key_points = []

    if document_type == "invoice":
        if structured_data.get("invoice_number"):
            key_points.append(f"Invoice Number: {structured_data.get('invoice_number')}")
        if structured_data.get("total_amount"):
            key_points.append(f"Total Amount: {structured_data.get('total_amount')}")
        if structured_data.get("date"):
            key_points.append(f"Invoice Date: {structured_data.get('date')}")

    elif document_type == "resume":
        if structured_data.get("email"):
            key_points.append(f"Email: {structured_data.get('email')}")
        if structured_data.get("phone"):
            key_points.append(f"Phone: {structured_data.get('phone')}")
        if structured_data.get("skills"):
            key_points.append(f"Skills: {', '.join(structured_data.get('skills', []))}")

    elif document_type == "contract":
        if structured_data.get("effective_date"):
            key_points.append(f"Effective Date: {structured_data.get('effective_date')}")
        if structured_data.get("parties"):
            key_points.append(f"Parties: {', '.join(structured_data.get('parties', []))}")
        if structured_data.get("termination"):
            key_points.append(f"Termination: {structured_data.get('termination')[:200]}")

    elif document_type == "report":
        if structured_data.get("title"):
            key_points.append(f"Title: {structured_data.get('title')}")
        if structured_data.get("summary"):
            key_points.append(f"Embedded Summary: {structured_data.get('summary')[:250]}")

    else:
        key_points.append("Document uploaded and processed successfully.")
        if cleaned:
            key_points.append(f"Preview: {cleaned[:200]}")

    if not key_points and cleaned:
        key_points = [cleaned[:250]]

    if document_type == "invoice":
        recommended_next_action = "Validate invoice amount, due date, and payment workflow."
    elif document_type == "resume":
        recommended_next_action = "Review candidate profile and compare skills against job requirements."
    elif document_type == "contract":
        recommended_next_action = "Review obligations, dates, and termination clauses before approval."
    elif document_type == "report":
        recommended_next_action = "Review findings and convert insights into action items."
    else:
        recommended_next_action = "Review the extracted content and classify it further if needed."

    return {
        "summary": short_summary,
        "key_points": key_points[:5],
        "recommended_next_action": recommended_next_action
    }