import re


def extract_invoice_data(text: str) -> dict:
    invoice_number = None
    total_amount = None
    date = None

    invoice_match = re.search(r"(invoice number|invoice no\.?|invoice #)\s*[:\-]?\s*([A-Za-z0-9\-]+)", text, re.IGNORECASE)
    if invoice_match:
        invoice_number = invoice_match.group(2)

    total_match = re.search(r"(total due|total|amount due)\s*[:\-]?\s*\$?\s*([\d,]+(?:\.\d{2})?)", text, re.IGNORECASE)
    if total_match:
        total_amount = total_match.group(2)

    date_match = re.search(r"(date)\s*[:\-]?\s*([0-9]{1,2}[\/\-][0-9]{1,2}[\/\-][0-9]{2,4})", text, re.IGNORECASE)
    if date_match:
        date = date_match.group(2)

    return {
        "invoice_number": invoice_number,
        "total_amount": total_amount,
        "date": date
    }


def extract_resume_data(text: str) -> dict:
    email = None
    phone = None
    skills = []

    email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    if email_match:
        email = email_match.group(0)

    phone_match = re.search(r'(\+?\d{1,2}[\s\-]?)?(\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4})', text)
    if phone_match:
        phone = phone_match.group(0)

    common_skills = [
        "python", "java", "sql", "javascript", "typescript",
        "react", "fastapi", "machine learning", "deep learning",
        "postgresql", "aws", "azure", "git", "docker"
    ]

    lower_text = text.lower()
    for skill in common_skills:
        if skill in lower_text:
            skills.append(skill)

    return {
        "email": email,
        "phone": phone,
        "skills": skills
    }


def extract_contract_data(text: str) -> dict:
    effective_date = None
    parties = []
    termination = None

    effective_match = re.search(r"(effective date)\s*[:\-]?\s*([A-Za-z0-9,\/\- ]+)", text, re.IGNORECASE)
    if effective_match:
        effective_date = effective_match.group(2).strip()

    termination_match = re.search(r"(termination.*)", text, re.IGNORECASE)
    if termination_match:
        termination = termination_match.group(1).strip()

    party_matches = re.findall(r"between\s+([A-Za-z0-9 &.,]+)\s+and\s+([A-Za-z0-9 &.,]+)", text, re.IGNORECASE)
    if party_matches:
        for match in party_matches:
            parties.extend([match[0].strip(), match[1].strip()])

    return {
        "effective_date": effective_date,
        "parties": parties,
        "termination": termination
    }


def extract_report_data(text: str) -> dict:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    title = lines[0] if lines else None

    summary = None
    summary_match = re.search(
        r"(executive summary|summary)(.*?)(introduction|findings|conclusion|$)",
        text,
        re.IGNORECASE | re.DOTALL
    )
    if summary_match:
        summary = summary_match.group(2).strip()[:1000]

    return {
        "title": title,
        "summary": summary
    }


def extract_document_data(document_type: str, text: str) -> dict:
    if document_type == "invoice":
        return extract_invoice_data(text)
    elif document_type == "resume":
        return extract_resume_data(text)
    elif document_type == "contract":
        return extract_contract_data(text)
    elif document_type == "report":
        return extract_report_data(text)
    else:
        return {}