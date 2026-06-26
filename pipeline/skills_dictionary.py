AI_SKILLS = {
    "languages": ["python", "r programming", "julia"],
    "classical_ml": [
        "machine learning", "regression", "classification", "decision tree",
        "random forest", "xgboost", "lightgbm", "catboost", "svm",
        "clustering", "k-means", "dbscan", "pca", "feature engineering",
        "cross-validation", "scikit-learn", "sklearn"
    ],
    "deep_learning": [
        "deep learning", "neural network", "cnn", "convolutional",
        "rnn", "lstm", "gru", "transformer", "transfer learning",
        "autoencoder", "gan", "diffusion model", "pytorch", "tensorflow", "keras"
    ],
    "genai_llm": [
        "llm", "large language model", "generative ai", "genai",
        "prompt engineering", "rag", "retrieval augmented generation",
        "embeddings", "vector database", "faiss", "pinecone", "chroma",
        "fine-tuning", "lora", "langchain", "llamaindex", "agentic",
        "function calling", "hugging face", "transformers library"
    ],
    "cv_nlp": [
        "computer vision", "opencv", "object detection", "image segmentation",
        "nlp", "natural language processing", "sentiment analysis",
        "speech recognition", "text-to-speech", "mediapipe"
    ],
    "mlops": [
        "mlops", "model serving", "mlflow", "weights and biases",
        "model deployment", "model monitoring", "quantization"
    ],
    "data": [
        "pandas", "numpy", "data preprocessing", "etl", "data pipeline",
        "data cleaning", "spark", "hadoop"
    ],
}

BACKEND_SKILLS = {
    "languages": [
        "python", "java", "javascript", "typescript", "node.js", "nodejs",
        "c#", ".net", "golang", " go ", "php", "ruby"
    ],
    "frameworks": [
        "fastapi", "django", "flask", "express.js", "expressjs",
        "spring boot", "asp.net", ".net core", "nestjs", "laravel"
    ],
    "core_concepts": [
        "rest api", "restful", "graphql", "client-server", "authentication",
        "authorization", "jwt", "oauth", "middleware", "caching", "redis",
        "rate limiting", "webhook", "message queue", "rabbitmq", "kafka", "sqs"
    ],
    "databases": [
        "sql", "postgresql", "postgres", "mysql", "sql server", "mongodb",
        "nosql", "dynamodb", "cassandra", "orm", "sqlalchemy", "entity framework",
        "database indexing", "database migration"
    ],
    "system_design": [
        "microservices", "monolithic", "load balancing", "api gateway",
        "horizontal scaling", "vertical scaling", "database sharding"
    ],
    "devops": [
        "docker", "kubernetes", "ci/cd", "github actions", "jenkins",
        "aws", "azure", "gcp", "nginx", "prometheus", "grafana"
    ],
    "testing": [
        "unit testing", "pytest", "junit", "jest", "tdd", "integration testing", "mocking"
    ],
}

# Languages/frameworks that, if explicitly required and NOT in the resume,
# should hard-disqualify a role (the Klubworks/Enan Tech problem).
LANGUAGE_SIGNALS = {
    "python": ["python", "django", "flask", "fastapi"],
    "java": ["java ", "spring boot", "spring framework"],
    "javascript_node": ["javascript", "node.js", "nodejs", "express.js", "typescript", "nestjs"],
    "csharp_dotnet": ["c#", ".net", "asp.net"],
    "go": ["golang", " go "],
    "php": ["php", "laravel"],
    "ruby": ["ruby", "rails"],
}

def flatten(skill_dict):
    out = []
    for category in skill_dict.values():
        out.extend(category)
    return out

ALL_AI_SKILLS = flatten(AI_SKILLS)
ALL_BACKEND_SKILLS = flatten(BACKEND_SKILLS)
ALL_SKILLS = list(set(ALL_AI_SKILLS + ALL_BACKEND_SKILLS))


def extract_matched_skills(text, skill_list):
    text_lower = text.lower()
    return sorted(set(s.strip() for s in skill_list if s.strip() in text_lower))


def detect_required_languages(jd_text):
    """Returns which language-families the JD explicitly requires."""
    text_lower = jd_text.lower()
    required = []
    for lang_family, signals in LANGUAGE_SIGNALS.items():
        if any(sig in text_lower for sig in signals):
            required.append(lang_family)
    return required


def candidate_has_language(resume_text, lang_family):
    text_lower = resume_text.lower()
    signals = LANGUAGE_SIGNALS.get(lang_family, [])
    return any(sig in text_lower for sig in signals)