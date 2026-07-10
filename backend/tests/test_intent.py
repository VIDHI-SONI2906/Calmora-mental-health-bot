import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from nlu_utils import extract_intent

test_cases = [
    # loneliness
    ("I feel so isolated lately.", "loneliness"),
    ("I don't really have anyone close to me anymore.", "loneliness"),

    # depression
    ("I feel worthless and empty inside.", "depression"),
    ("Nothing feels enjoyable to me anymore.", "depression"),

    # anxiety
    ("I've been worried about everything lately.", "anxiety"),
    ("I can't stop feeling on edge all day.", "anxiety"),

    # stress
    ("I can't cope with things right now.", "stress"),
    ("Everything feels like too much pressure lately.", "stress"),

    # ptsd
    ("I had a nightmare again last night.", "ptsd"),
    ("I keep getting triggered by loud noises since the accident.", "ptsd"),

    # grief
    ("I've been mourning my grandfather's death.", "grief"),
    ("It's been hard since my mom passed away.", "grief"),

    # addiction
    ("My gambling has become a real problem.", "addiction"),
    ("I can't stop drinking even when I want to.", "addiction"),

    # relationship
    ("I feel really jealous in my relationship lately.", "relationship"),
    ("My partner and I keep arguing about everything.", "relationship"),

    # breakup
    ("I just got dumped and it really hurts.", "breakup"),
    ("My ex ended things and I'm struggling to move on.", "breakup"),

    # insomnia
    ("I've been tossing and turning all night.", "insomnia"),
    ("I haven't been sleeping well for weeks.", "insomnia"),

    # eating_disorder
    ("I've been purging after meals.", "eating_disorder"),
    ("I'm obsessed with counting calories every day.", "eating_disorder"),

    # self_harm
    ("I've been cutting myself when things get bad.", "self_harm"),
    ("I hurt myself when I feel overwhelmed.", "self_harm"),

    # suicide
    ("I want to kill myself.", "suicide"),
    ("I don't see a reason to keep living.", "suicide"),

    # substance_abuse
    ("I just got out of rehab and it's been hard.", "substance_abuse"),
    ("I've been taking too many pills lately.", "substance_abuse"),

    # bipolar
    ("I've been having racing thoughts and mood swings.", "bipolar"),
    ("My highs and lows have been really extreme lately.", "bipolar"),

    # schizophrenia
    ("I've been hearing voices lately that scare me.", "schizophrenia"),
    ("I feel like people are watching me and it's not real.", "schizophrenia"),

    # ocd
    ("I keep having intrusive thoughts I can't control.", "ocd"),
    ("I have to check the door lock over and over.", "ocd"),

    # burnout
    ("I've been dealing with emotional exhaustion and feel completely overextended.", "burnout"),
    ("I'm so burned out I can barely function at work.", "burnout"),

    # panic
    ("I started hyperventilating and couldn't catch my breath.", "panic"),
    ("My chest felt tight and I thought I was dying.", "panic"),

    # trauma
    ("I'm still dealing with childhood trauma from years ago.", "trauma"),
    ("That accident really traumatized me.", "trauma"),
]

@pytest.mark.parametrize("message,expected_intent", test_cases)
def test_intent_classification(message, expected_intent):
    predicted = extract_intent(message)
    assert predicted == expected_intent, f"'{message}' → expected {expected_intent}, got {predicted}"