import re
from spellchecker import SpellChecker

# 1. Initialize Spell Checker
spell = SpellChecker()

# 2. The Master Whitelist (Technical & Business Terms)
# These words are considered "Correct" even if English dictionaries disagree.
TECH_TERMS = {
    # Roles & Titles
    "manager", "management", "developer", "development", "engineer", "engineering",
    "analyst", "analysis", "analytics", "consultant", "specialist", "architect",
    "associate", "director", "president", "partner", "founder", "co-founder",
    "admin", "administrator", "intern", "internship", "freelancer", "executive",
    
    # Core Tech
    "python", "java", "javascript", "typescript", "react", "angular", "vue",
    "html", "css", "django", "flask", "fastapi", "kubernetes", "docker",
    "aws", "azure", "linux", "unix", "mysql", "postgresql", "mongodb",
    "redis", "elasticsearch", "git", "github", "gitlab", "jenkins",
    "tensorflow", "pytorch", "pandas", "numpy", "scikit-learn", "tableau",
    "powerbi", "excel", "agile", "scrum", "jira", "confluence",
    "c++", "c#", ".net", "php", "ruby", "golang", "swift", "kotlin", "scala",
    "node", "nodejs", "express", "spring", "boot", "hibernate", "jpa",
    "ios", "android", "mobile", "web", "cloud", "data", "code", "stack",
    
    # Industry Acronyms & Jargon (Crucial!)
    "sql", "nosql", "api", "rest", "restful", "soap", "graphql",
    "ci/cd", "devops", "mlops", "saas", "paas", "iaas", "fintech", "edtech",
    "medtech", "adtech", "martech", "mvp", "poc", "kpi", "okr", "roi",
    "b2b", "b2c", "seo", "sem", "crm", "erp", "cms", "lms", "ats",
    "ui", "ux", "gui", "cli", "ide", "sdk", "npm", "pip",
    "gcp", "s3", "ec2", "lambda", "rds", "vpc", "iam",
    "ma", "ms", "ba", "bs", "phd", "mba", "gpa", "btech", "mtech",
    "gamification", "scalability", "latency", "throughput", "bandwidth",
    "underserved", "onboarding", "lifecycle", "stakeholder", "roadmap",
    "backend", "frontend", "serverless", "microservices", "workflow", "pipeline",
    "app", "apps" # Explicitly protect "App" from becoming "Ape"
}

# Load whitelist into the spellchecker so it knows them
spell.word_frequency.load_words(TECH_TERMS)

# 3. OCR Shape Fixer (Visual Typos)
# Fixes errors where letters look similar (e.g. 'rn' vs 'm')
OCR_SHAPE_FIXES = {
    "avs": "aws",       # V vs W
    "lwo": "two",       # l vs t
    "iy": "ly",         # I vs l
    "rn": "m",          # rn vs m
    "vv": "w",          # vv vs w
    "clod": "cloud",    # o vs ou
    "fer": "for",       # e vs o
    "cops": "cgpa",     # OCR often reads CGPA as Cops
    "redst": "redshift",
    "sol": "sql",       # S-O-L vs S-Q-L
    "finch": "fintech", # Auto-correct hallucination
    "ape": "app",       # Auto-correct hallucination
    "map": "mvp",       # Auto-correct hallucination
    "clip": "cli"       # Auto-correct hallucination
}

def fix_ocr_shapes(text):
    """
    Step 1: Fix Visual OCR errors before spellcheck runs.
    """
    tokens = text.split()
    fixed = []
    for token in tokens:
        lower = token.lower()
        # Clean punctuation for lookup (e.g. "AWS," -> "aws")
        clean = re.sub(r'[^a-z]', '', lower)
        
        if clean in OCR_SHAPE_FIXES:
            correction = OCR_SHAPE_FIXES[clean]
            # Smart Case Restoration
            if token.isupper(): correction = correction.upper()
            elif token.istitle(): correction = correction.title()
            fixed.append(correction)
        else:
            fixed.append(token)
    return " ".join(fixed)

def fix_typos_smart(text):
    """
    Step 2: Conservative Spell Checker.
    Only fixes words that are definitely wrong and definitely NOT technical terms.
    """
    if not text: return ""
    tokens = text.split(' ')
    fixed_tokens = []
    
    for token in tokens:
        # Strip punctuation for checking
        # Allow technical symbols: +, #, -, ., /
        clean_token = re.sub(r'[^a-zA-Z0-9+#\-\./]', '', token)
        clean_lower = clean_token.lower()
        
        if not clean_lower:
            fixed_tokens.append(token); continue

        # --- THE SHIELDS (Prevent Bad Corrections) ---
        
        # 1. Acronym Shield: ALL CAPS > 1 letter (e.g. "SQL", "AWS")
        if clean_token.isupper() and len(clean_token) > 1: 
            fixed_tokens.append(token); continue
            
        # 2. CamelCase Shield: Mixed Case (e.g. "GitHub", "PowerBI")
        if any(c.islower() for c in clean_token) and any(c.isupper() for c in clean_token): 
            fixed_tokens.append(token); continue
            
        # 3. Short Word Fence: Don't touch words <= 3 chars unless crucial (e.g. "Git", "App")
        if len(clean_token) <= 3: 
            fixed_tokens.append(token); continue
            
        # 4. Dictionary Shield: Is it in English OR our Tech List?
        if clean_lower in TECH_TERMS or clean_lower in spell: 
            fixed_tokens.append(token); continue
            
        # 5. Data Shield: Numbers or Emails
        if any(char.isdigit() for char in clean_token) or '@' in token: 
            fixed_tokens.append(token); continue

        # --- CORRECTION LOGIC ---
        correction = spell.correction(clean_lower)
        
        # Only accept correction if valid (not None) AND it's a known word
        if correction and (correction in spell or correction in TECH_TERMS):
            # Match original casing (Title Case)
            if token[0].isupper(): correction = correction.title()
            fixed_tokens.append(correction)
        else:
            # If unsure, keep the original. Better a typo than a wrong word.
            fixed_tokens.append(token)
            
    return " ".join(fixed_tokens)

def clean_text(raw_text):
    """
    Master Cleaning Pipeline
    """
    if not raw_text: return ""

    text = raw_text
    
    # 1. Layout Fix: Standardize Bullets
    text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219*+>|]', '\n', text)
    
    # 2. Sanitize: Allow text, newlines, and technical symbols
    text = re.sub(r'[^\x00-\x7F\n]+', ' ', text) 
    
    # 3. Visual Fixes (OCR Shapes)
    text = fix_ocr_shapes(text)
    
    # 4. Smart Spellcheck
    text = fix_typos_smart(text)
    
    # 5. Spacing Consistency
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n\s*\n', '\n', text).strip()
    
    return text