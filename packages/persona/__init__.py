"""
Persona Intelligence Layer for Alisha AI Friend.

This package builds, stores, and queries the complete behavioral DNA of the target person
from the real corpus. Every module is evidence-grounded, not assumed.

Modules:
    analyzer.py         — Runs full corpus analysis, outputs all profile files
    emoji_engine.py     — Conditional emoji model
    slang_engine.py     — Auto-discovered slang lexicon
    address_engine.py   — Nickname / address term model
    humor_engine.py     — Humor type fingerprint
    response_act.py     — Speech act classifier and profile
    burst_engine.py     — Message burst distribution model
    drift_engine.py     — Temporal style drift detector
    loader.py           — Fast profile loader used by all other packages
"""
