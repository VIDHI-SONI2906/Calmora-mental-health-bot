# backend/nlu_utils.py

import spacy
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load the spaCy English model
nlp = spacy.load("en_core_web_sm")

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

# Expanded keywords for mental health conditions
INTENT_KEYWORDS = {
    "loneliness": ["lonely", "alone", "isolated", "no friends", "isolation", "no one to talk to", "feel alone", 
                   "solitude", "abandoned", "disconnected", "outcast", "excluded"],
    "depression": ["depressed", "depression", "sad", "hopeless", "unmotivated", "numb", "empty", "unhappy", 
                   "melancholy", "despair", "miserable", "worthless", "pointless", "can't enjoy", "no pleasure", 
                   "don't care anymore", "no interest", "everything is hard"],
    "anxiety": ["anxious", "anxiety", "worried", "panic", "nervous", "stressed", "overwhelmed", "fear", "dread", 
                "on edge", "restless", "tense", "uneasy", "worried", "apprehensive", "can't relax", "constant worry"],
    "stress": ["stress", "stressed", "overwhelmed", "burnout", "burned out", "can't cope", "pressure", "too much", 
               "exhausted", "drained", "overloaded", "stretched thin"],
    "ptsd": ["trauma", "traumatic", "flashback", "nightmare", "ptsd", "triggered", "abuse", "abused", "assault", 
             "combat", "accident", "traumatized", "reliving", "hypervigilant"],
    "grief": ["grief", "grieving", "loss", "lost", "died", "death", "passed away", "mourning", "bereavement", 
              "missing someone", "deceased", "funeral"],
    "addiction": ["addiction", "addicted", "substance", "alcohol", "drinking", "drugs", "gambling", "can't stop", 
                  "dependency", "withdrawal", "relapse", "sober", "recovery", "using again"],
    "relationship": ["relationship", "partner", "marriage", "spouse", "boyfriend", "girlfriend", "husband", "wife", 
                     "dating", "fight", "arguing", "conflict", "trust issues", "jealous", "commitment", "communication problems"],
    "breakup": ["breakup", "broke up", "divorce", "separated", "ex", "dumped", "left me", "ended relationship", 
                "heartbreak", "getting over", "split up", "called it off"],
    "insomnia": ["insomnia", "can't sleep", "sleep problems", "awake", "tossing and turning", "sleep deprived", 
                  "exhausted", "fatigue", "tired", "sleepless", "not sleeping well", "waking up"],
    "eating_disorder": ["eating disorder", "anorexia", "bulimia", "binge eating", "purging", "body image", "overweight", 
                        "underweight", "diet", "starving", "calories", "food issues", "weight obsession", "hate my body"],
    "self_harm": ["self harm", "cutting", "hurt myself", "harming myself", "injure myself", "self injury", 
                   "burning myself", "self-destructive", "self-inflicted", "self-mutilation"],
    "suicide": ["suicide", "suicidal", "kill myself", "end my life", "take my life", "want to die", 
                 "better off dead", "no reason to live", "can't go on", "too painful to live", "ending it all"],
    "substance_abuse": ["substance abuse", "drinking too much", "alcoholic", "drug problem", "high", "withdrawal", 
                        "addiction", "pills", "overdose", "detox", "rehab", "intoxicated", "needle", "using"],
    "bipolar": ["bipolar", "mania", "manic", "mood swings", "mood disorder", "highs and lows", "euphoria", 
                "grandiose", "impulsive", "racing thoughts"],
    "schizophrenia": ["schizophrenia", "psychosis", "hallucination", "delusion", "paranoia", "hearing voices", 
                      "seeing things", "thought disorder", "disorganized thinking"],
    "ocd": ["ocd", "obsessive", "compulsive", "intrusive thoughts", "rituals", "checking", "contamination", 
            "symmetry", "orderliness", "perfectionism", "rumination", "can't stop thinking about"],
    "burnout": ["burnout", "burned out", "exhausted", "overworked", "workaholic", "no energy", "chronic fatigue",
                "compassion fatigue", "emotional exhaustion", "overextended", "job stress"],
    "panic": ["panic attack", "heart racing", "can't breathe", "hyperventilating", "chest pain", "dying", 
              "emergency", "losing control", "sudden fear", "shortness of breath"],
    "trauma": ["trauma", "traumatic event", "abuse", "assault", "violence", "accident", "disaster", 
               "frightening experience", "emotional trauma", "childhood trauma"]
}

def extract_intent(user_message):
    """
    Enhanced rule-based intent classifier with expanded mental health topics.
    Returns the most specific matching intent based on keyword analysis.
    """
    lower_msg = user_message.lower()
    
    # First check for suicide intent as highest priority
    for keyword in INTENT_KEYWORDS["suicide"]:
        if keyword in lower_msg:
            return "suicide"
    
    # Track matches and their counts to find the most specific intent
    matches = {}
    
    for intent, keywords in INTENT_KEYWORDS.items():
        count = 0
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', lower_msg):
                count += 1
        if count > 0:
            matches[intent] = count
    
    # If we found matches, return the intent with the most keyword matches
    if matches:
        return max(matches.items(), key=lambda x: x[1])[0]
    
    # Default to general if no matches found
    return "general"

def extract_entities(user_message):
    """
    Extract entities from the message using spaCy.
    """
    doc = nlp(user_message)
    return {ent.label_: ent.text for ent in doc.ents}

def analyze_sentiment(user_message):
    """
    Return the compound sentiment score using VADER.
    Score ranges from -1 (very negative) to +1 (very positive).
    """
    scores = analyzer.polarity_scores(user_message)
    return scores["compound"]

def get_follow_up_question(intent):
    """
    Returns None - follow-up questions have been disabled.
    """
    return None