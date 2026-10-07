import re
from typing import Dict, List, Optional, Tuple, Any

# India tech hub cities and states
INDIAN_CITIES = {
    "delhi": ("Delhi", "Delhi"),
    "new delhi": ("New Delhi", "Delhi"),
    "noida": ("Noida", "Uttar Pradesh"),
    "greater noida": ("Greater Noida", "Uttar Pradesh"),
    "gurgaon": ("Gurugram", "Haryana"),
    "gurugram": ("Gurugram", "Haryana"),
    "bengaluru": ("Bengaluru", "Karnataka"),
    "bangalore": ("Bengaluru", "Karnataka"),
    "hyderabad": ("Hyderabad", "Telangana"),
    "mumbai": ("Mumbai", "Maharashtra"),
    "pune": ("Pune", "Maharashtra"),
    "chennai": ("Chennai", "Tamil Nadu"),
    "kolkata": ("Kolkata", "West Bengal"),
    "ahmedabad": ("Ahmedabad", "Gujarat"),
    "lucknow": ("Lucknow", "Uttar Pradesh"),
    "moradabad": ("Moradabad", "Uttar Pradesh"),
    "jaipur": ("Jaipur", "Rajasthan"),
    "chandigarh": ("Chandigarh", "Punjab"),
    "indore": ("Indore", "Madhya Pradesh"),
    "kochi": ("Kochi", "Kerala"),
    "thiruvananthapuram": ("Thiruvananthapuram", "Kerala"),
    "coimbatore": ("Coimbatore", "Tamil Nadu"),
}

# Skill dictionary: Canonical name -> list of aliases & synonyms
SKILL_TAXONOMY: Dict[str, Dict[str, Any]] = {
    # Programming languages
    "Python": {
        "category": "Language",
        "aliases": ["python", "python3", "py"],
    },
    "JavaScript": {
        "category": "Language",
        "aliases": ["javascript", "js", "ecmascript", "es6", "vanilla js"],
    },
    "TypeScript": {
        "category": "Language",
        "aliases": ["typescript", "ts"],
    },
    "Java": {
        "category": "Language",
        "aliases": ["java", "core java", "j2ee"],
    },
    "C++": {
        "category": "Language",
        "aliases": ["c++", "cpp"],
    },
    "C#": {
        "category": "Language",
        "aliases": ["c#", "csharp"],
    },
    "Golang": {
        "category": "Language",
        "aliases": ["go", "golang"],
    },
    "PHP": {
        "category": "Language",
        "aliases": ["php"],
    },
    "Bash": {
        "category": "Language",
        "aliases": ["bash", "shell scripting", "shell script"],
    },
    "SQL": {
        "category": "Database",
        "aliases": ["sql", "rdbms", "relational database"],
    },

    # Backend / frontend
    "FastAPI": {
        "category": "Framework",
        "aliases": ["fastapi", "fast api", "fast-api"],
    },
    "Django": {
        "category": "Framework",
        "aliases": ["django", "django rest framework", "drf"],
    },
    "Flask": {
        "category": "Framework",
        "aliases": ["flask"],
    },
    "React": {
        "category": "Framework",
        "aliases": ["react", "react.js", "reactjs", "react js"],
    },
    "Node.js": {
        "category": "Framework",
        "aliases": ["node", "node.js", "nodejs", "node js"],
    },
    "Express.js": {
        "category": "Framework",
        "aliases": ["express", "express.js", "expressjs"],
    },
    "Next.js": {
        "category": "Framework",
        "aliases": ["next.js", "nextjs", "next js"],
    },
    "Vue.js": {
        "category": "Framework",
        "aliases": ["vue", "vue.js", "vuejs"],
    },
    "Angular": {
        "category": "Framework",
        "aliases": ["angular", "angularjs"],
    },

    # Databases
    "PostgreSQL": {
        "category": "Database",
        "aliases": ["postgresql", "postgres", "psql"],
    },
    "MySQL": {
        "category": "Database",
        "aliases": ["mysql", "mariadb"],
    },
    "MongoDB": {
        "category": "Database",
        "aliases": ["mongodb", "mongo", "nosql"],
    },
    "Redis": {
        "category": "Database",
        "aliases": ["redis", "in-memory cache"],
    },
    "SQLite": {
        "category": "Database",
        "aliases": ["sqlite", "sqlite3"],
    },

    # DevOps / Cloud
    "Docker": {
        "category": "DevOps",
        "aliases": ["docker", "containerization", "containers"],
    },
    "Kubernetes": {
        "category": "DevOps",
        "aliases": ["kubernetes", "k8s"],
    },
    "AWS": {
        "category": "Cloud",
        "aliases": ["aws", "amazon web services", "ec2", "s3", "lambda"],
    },
    "GCP": {
        "category": "Cloud",
        "aliases": ["gcp", "google cloud", "google cloud platform"],
    },
    "Azure": {
        "category": "Cloud",
        "aliases": ["azure", "microsoft azure"],
    },
    "Git": {
        "category": "Tool",
        "aliases": ["git"],
    },
    "GitHub": {
        "category": "Tool",
        "aliases": ["github"],
    },
    "GitLab": {
        "category": "Tool",
        "aliases": ["gitlab"],
    },
    "CI/CD": {
        "category": "DevOps",
        "aliases": [
            "ci/cd",
            "ci cd",
            "continuous integration",
            "github actions",
            "jenkins",
        ],
    },

    # Architecture
    "REST API": {
        "category": "Architecture",
        "aliases": ["rest", "restful", "rest api", "rest apis", "restful api"],
    },
    "GraphQL": {
        "category": "Architecture",
        "aliases": ["graphql", "graph ql"],
    },

    # Security
    "Cybersecurity": {
        "category": "Security",
        "aliases": [
            "cybersecurity",
            "cyber security",
            "infosec",
        ],
    },
    "Penetration Testing": {
        "category": "Security",
        "aliases": [
            "penetration testing",
            "penetration test",
            "pentesting",
            "pen testing",
            "pentest",
        ],
    },
    "Vulnerability Assessment": {
        "category": "Security",
        "aliases": [
            "vulnerability assessment",
            "vulnerability assessments",
        ],
    },
    "Vulnerability Management": {
        "category": "Security",
        "aliases": [
            "vulnerability management",
        ],
    },
    "Nmap": {
        "category": "Security Tool",
        "aliases": ["nmap"],
    },
    "Metasploit": {
        "category": "Security Tool",
        "aliases": ["metasploit", "metasploit framework"],
    },
    "Burp Suite": {
        "category": "Security Tool",
        "aliases": ["burp suite", "burpsuite"],
    },
    "Nikto": {
        "category": "Security Tool",
        "aliases": ["nikto"],
    },
    "OWASP ZAP": {
        "category": "Security Tool",
        "aliases": [
            "owasp zap",
            "owasp zap proxy",
            "zaproxy",
            "zap proxy",
        ],
    },
    "Gobuster": {
        "category": "Security Tool",
        "aliases": ["gobuster"],
    },
    "Wireshark": {
        "category": "Security Tool",
        "aliases": ["wireshark"],
    },
    "CyberChef": {
        "category": "Security Tool",
        "aliases": ["cyberchef", "cyber chef"],
    },
    "SIEM": {
        "category": "Security",
        "aliases": ["siem", "siem tools"],
    },
    "Firewalls": {
        "category": "Security",
        "aliases": ["firewall", "firewalls"],
    },
    "OWASP Top 10": {
        "category": "Security",
        "aliases": ["owasp top 10", "owasp top ten"],
    },
    "CVE Analysis": {
        "category": "Security",
        "aliases": ["cve analysis", "cve analysis and assessment"],
    },

    # Operating systems
    "Linux": {
        "category": "System",
        "aliases": ["linux", "ubuntu", "debian", "centos"],
    },
    "Windows": {
        "category": "System",
        "aliases": ["windows", "windows os", "microsoft windows"],
    },
    "Kali Linux": {
    "aliases": ["kali linux"],
    "category": "System",
},

    # AI / ML
    "Machine Learning": {
        "category": "AI/ML",
        "aliases": ["machine learning", "ml", "deep learning"],
    },
    "PyTorch": {
        "category": "AI/ML",
        "aliases": ["pytorch", "torch"],
    },
    "TensorFlow": {
        "category": "AI/ML",
        "aliases": ["tensorflow", "tf", "keras"],
    },
    "NLP": {
        "category": "AI/ML",
        "aliases": [
            "nlp",
            "natural language processing",
            "llm",
            "llms",
            "large language models",
        ],
    },

    # Frontend
    "HTML": {
        "category": "Frontend",
        "aliases": ["html", "html5"],
    },
    "CSS": {
        "category": "Frontend",
        "aliases": [
            "css",
            "css3",
            "sass",
            "scss",
            "tailwind",
            "bootstrap",
        ],
    },
}

# Inverted index for fast normalization lookup
ALIAS_TO_CANONICAL: Dict[str, str] = {}
for canonical, data in SKILL_TAXONOMY.items():
    ALIAS_TO_CANONICAL[canonical.lower()] = canonical
    for alias in data["aliases"]:
        ALIAS_TO_CANONICAL[alias.lower()] = canonical


class JobNormalizer:
    @staticmethod
    def normalize_skill(skill_str: str) -> Optional[Tuple[str, str]]:
        """
        Normalize skill string to canonical name and category.
        e.g. 'js' -> ('JavaScript', 'Language')
        """
        cleaned = skill_str.strip().lower()
        if cleaned in ALIAS_TO_CANONICAL:
            canon = ALIAS_TO_CANONICAL[cleaned]
            category = SKILL_TAXONOMY[canon]["category"]
            return canon, category
        
        # Exact match or title cased match for unknown technologies
        cleaned_cap = skill_str.strip().title()
        return cleaned_cap, "General"

    @staticmethod
    def extract_skills_from_text(text: str) -> List[Dict[str, str]]:
        """
        Extract canonical skills from text using the centralized taxonomy.

        Longer/more specific aliases are checked first so that:
            "penetration testing" -> Penetration Testing
        instead of:
            "penetration testing" -> Cybersecurity
        """

        found = {}

        if not text:
            return []

        text_normalized = re.sub(r"\s+", " ", text.lower()).strip()

        # Check longer aliases first.
        aliases = sorted(
            ALIAS_TO_CANONICAL.items(),
            key=lambda item: len(item[0]),
            reverse=True,
        )

        for alias, canonical in aliases:
            escaped_alias = re.escape(alias)

            # Word boundaries prevent things such as:
            # "go" matching "google".
            pattern = rf"(?<!\w){escaped_alias}(?!\w)"

            if re.search(pattern, text_normalized, re.IGNORECASE):
                category = SKILL_TAXONOMY[canonical]["category"]

                found[canonical] = {
                    "name": canonical,
                    "canonical_name": canonical,
                    "category": category,
                }

        return list(found.values())

    @staticmethod
    def normalize_location(raw_loc: Optional[str]) -> Tuple[str, Optional[str], Optional[str], str]:
        """
        Returns (location_label, city, state, remote_status)
        """
        if not raw_loc:
            return "India", None, None, "On-site"
            
        loc_clean = raw_loc.strip()
        loc_lower = loc_clean.lower()
        
        remote_status = "On-site"
        if "remote" in loc_lower or "work from home" in loc_lower or "wfh" in loc_lower:
            remote_status = "Remote"
        elif "hybrid" in loc_lower:
            remote_status = "Hybrid"

        # Check against Indian cities
        detected_city = None
        detected_state = None
        for key, (city, state) in INDIAN_CITIES.items():
            if key in loc_lower:
                detected_city = city
                detected_state = state
                break
                
        if remote_status == "Remote":
            if detected_city:
                display_loc = f"Remote ({detected_city}, India)"
            else:
                display_loc = "Remote India"
        elif detected_city and detected_state:
            display_loc = f"{detected_city}, {detected_state}"
        else:
            display_loc = loc_clean if loc_clean else "India"

        return display_loc, detected_city, detected_state, remote_status

    @staticmethod
    def normalize_salary(salary_min: Optional[float], salary_max: Optional[float], currency: Optional[str] = "INR") -> Tuple[Optional[float], Optional[float], str]:
        """
        Normalizes salary into annual INR where possible.
        """
        curr = currency.upper() if currency else "INR"
        # If monthly salary is detected (< 200,000 INR), convert to annual
        s_min = salary_min
        s_max = salary_max
        if s_min and s_min > 0 and s_min < 200000 and curr == "INR":
            # Likely monthly in INR
            s_min = s_min * 12
        if s_max and s_max > 0 and s_max < 200000 and curr == "INR":
            s_max = s_max * 12
            
        return s_min, s_max, curr

    @staticmethod
    def normalize_title(title: str) -> str:
        """
        Normalizes title by removing noisy recruiter buzzwords.
        """
        clean = re.sub(r"(?i)\b(urgent|urgently hiring|immediate joiner|hiring for|wanted|opening for)\b", "", title)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean.title() if clean else title.title()

    @staticmethod
    def extract_experience_years(text: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Extracts minimum and maximum years of experience required from text.
        e.g. '3-5 years', 'at least 2 yrs', '5+ years'
        """
        # Pattern: 3 to 5 years, 3-5 yrs, 2+ years, 5 years
        match = re.search(r"(\d+)\s*(?:-|to)\s*(\d+)\s*(?:\+)?\s*(?:years|year|yrs|yr)", text, re.IGNORECASE)
        if match:
            return float(match.group(1)), float(match.group(2))
            
        match_plus = re.search(r"(\d+)\s*(?:\+)\s*(?:years|year|yrs|yr)", text, re.IGNORECASE)
        if match_plus:
            return float(match_plus.group(1)), None

        match_single = re.search(r"(?:minimum|at least)?\s*(\d+)\s*(?:years|year|yrs|yr)", text, re.IGNORECASE)
        if match_single:
            return float(match_single.group(1)), None

        return None, None
