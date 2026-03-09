def classify_document(text: str) -> str:
    """
    Simple rule-based classifier for MVP stage.
    Later we can replace this with LLM-based classification.
    """
    if not text:
        return "unknown"

    lower_text = text.lower()

    invoice_keywords = [
        "invoice", "bill to", "amount due", "invoice number",
        "subtotal", "tax", "total due", "payment terms"
    ]

    resume_keywords = [
        "experience", "education", "skills", "projects",
        "linkedin", "github", "certifications", "summary"
    ]

    contract_keywords = [
        "agreement", "party", "parties", "terms and conditions",
        "effective date", "termination", "obligations", "confidentiality"
    ]

    report_keywords = [
        "executive summary", "introduction", "findings",
        "analysis", "conclusion", "recommendation", "methodology"
    ]

    def keyword_score(keywords):
        return sum(1 for word in keywords if word in lower_text)

    scores = {
        "invoice": keyword_score(invoice_keywords),
        "resume": keyword_score(resume_keywords),
        "contract": keyword_score(contract_keywords),
        "report": keyword_score(report_keywords),
    }

    best_match = max(scores, key=scores.get)

    if scores[best_match] == 0:
        return "unknown"

    return best_match