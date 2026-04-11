SENSITIVE_KEYWORDS = ["confidential", "secret", "private"]

def is_sensitive(file_path):
    return any(word in file_path.lower() for word in SENSITIVE_KEYWORDS)