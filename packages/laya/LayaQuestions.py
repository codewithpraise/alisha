"""
Laya Question Templates
Single-forward-pass typed questions for fast routing and behavior planning.
"""

from typing import Dict, Any, List

LAYA_ROUTING_QUESTIONS = [
    {
        "id": "response_mode",
        "question": "Does this user message require deep conversational processing with memory and graph RAG, a lightweight fast reply, or a low-latency voice call response?",
        "options": ["FAST", "DEEP", "CALL"]
    },
    {
        "id": "retrieval_need",
        "question": "What level of message corpus and memory retrieval is necessary to formulate an authentic reply?",
        "options": ["NONE", "LIGHT", "DEEP"]
    },
    {
        "id": "memory_need",
        "question": "Does the user message request to remember new facts, recall past facts, update existing info, forget something, or require no memory mutation?",
        "options": ["NONE", "RECALL", "WRITE", "UPDATE", "FORGET"]
    },
    {
        "id": "interaction_mode",
        "question": "What is the primary emotional or conversational posture of this interaction?",
        "options": ["CASUAL", "PLAYFUL", "TEASING", "AFFECTIONATE", "SUPPORTIVE", "SERIOUS", "EXCITED", "LOW_ENERGY", "FIRM", "FAREWELL"]
    },
    {
        "id": "response_act",
        "question": "What kind of conversational speech act should the persona perform in response?",
        "options": [
            "GREETING", "REACTION", "ANSWER", "QUESTION", "FOLLOW_UP", 
            "TEASE", "PLAYFUL_INSULT", "AFFECTION", "REASSURANCE", "COMFORT", 
            "ENCOURAGEMENT", "HUMOR", "EXPLANATION", "CORRECTION", "ACKNOWLEDGMENT", 
            "SURPRISE", "EXCITEMENT", "TOPIC_SHIFT", "FAREWELL"
        ]
    },
    {
        "id": "historical_reference",
        "question": "Does this message explicitly or implicitly reference shared past events, inside jokes, or historical interactions?",
        "options": ["TRUE", "FALSE"]
    }
]
