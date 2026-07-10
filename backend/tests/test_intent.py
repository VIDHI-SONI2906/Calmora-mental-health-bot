import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from nlu_utils import extract_intent

# Core suite: one test message per intent category, using the classifier's
# own keywords so results are reliable and not guesswork
core_cases = [
    ("I feel so isolated lately.", "loneliness"),
    ("I feel worthless and empty inside.", "depression"),
    ("I've been worried about everything lately.", "anxiety"),
    ("I can't cope with things right now.", "stress"),
    ("I had a nightmare again last night.", "ptsd"),
    ("I've been mourning my grandfather's death.", "grief"),
    ("My gambling has become a real problem.", "addiction"),
    ("I feel really jealous in my relationship lately.", "relationship"),
    ("I just got dumped and it really hurts.", "breakup"),
    ("I've been tossing and turning all night.", "insomnia"),
    ("I've been purging after meals.", "eating_disorder"),
    ("I've been cutting myself when things get bad.", "self_harm"),
    ("I want to kill myself.", "suicide"),
    ("I just got out of rehab and it's been hard.", "substance_abuse"),
    ("I've been having racing thoughts and mood swings.", "bipolar"),
    ("I've been hearing voices lately that scare me.", "schizophrenia"),
    ("I keep having intrusive thoughts I can't control.", "ocd"),
    ("I've been dealing with emotional exhaustion and feel completely overextended.", "burnout"),
    ("I started hyperventilating and couldn't catch my breath.", "panic"),
    ("I'm still dealing with childhood trauma from years ago.", "trauma"),
]

@pytest.mark.parametrize("message,expected_intent", core_cases)
def test_intent_classification_core(message, expected_intent):
    predicted = extract_intent(message)
    assert predicted == expected_intent, f"'{message}' → expected {expected_intent}, got {predicted}"


# Robustness cases: realistic paraphrases WITHOUT the exact trigger keywords.
# Marked xfail (expected to fail) since your classifier is keyword-based,
# not semantic — this documents a known, honest limitation rather than
# hiding it or inflating your accuracy number.
robustness_cases = [
    ("My heart is racing and I can't calm down.", "anxiety"),
    ("I don't have anyone to talk to.", "loneliness"),
    ("I miss my dad so much since he passed.", "grief"),
]

@pytest.mark.xfail(reason="Keyword-based classifier does not catch paraphrases without exact trigger words")
@pytest.mark.parametrize("message,expected_intent", robustness_cases)
def test_intent_classification_robustness(message, expected_intent):
    predicted = extract_intent(message)
    assert predicted == expected_intent, f"'{message}' → expected {expected_intent}, got {predicted}"