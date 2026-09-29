#!/usr/bin/env python3
"""
Regression Verification Suite for Alisha.
1. Runs the 8 frozen-eval prompts through the controller and asserts each matches FROZEN target.
2. Runs the free-form probe set.
3. Asserts no output contains banned leaks ("as an ai", "[end of text]", "<|im_", "user\n").
"""
import sys, os

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from alisha_controller import Alisha, FROZEN

FROZEN_PROMPTS = [
    ("i miss you", "mm i do too"),
    ("i miss u", "mm i do too"),
    ("miss u", "mm i do too"),
    ("miss you", "mm i do too"),
    ("youre so funny", "i know i know"),
    ("youre hilarious", "i know i know"),
    ("im bored", "me too"),
    ("hey what are you doing", "waiting on my dad"),
]

FREE_FORM_PROBES = [
    "what are you thinking about right now?",
    "did you eat today?",
    "are you still awake?",
    "what should i do?",
    "tell me something",
]

BANNED_SUBSTRINGS = [
    "as an ai",
    "[end of text]",
    "<|im_",
    "user\n",
]

def run_verification():
    print("=" * 60)
    print("ALISHA REGRESSION VERIFICATION SUITE")
    print("=" * 60)

    controller = Alisha()
    failures = 0

    print("\n--- 1. FROZEN EVAL (8 PROMPTS) ---")
    for prompt, expected in FROZEN_PROMPTS:
        controller.reset()
        actual = controller.reply(prompt)
        status = "PASS" if actual == expected else "FAIL"
        print(f"[{status}] Prompt: {prompt!r}")
        print(f"       Expected: {expected!r}")
        print(f"       Actual:   {actual!r}")
        if status != "PASS":
            failures += 1

    print("\n--- 2. FREE-FORM PROBES ---")
    for prompt in FREE_FORM_PROBES:
        controller.reset()
        actual = controller.reply(prompt)
        print(f"Prompt: {prompt!r}")
        print(f"Reply:  {actual!r}")

        # Check for banned substrings
        low = actual.lower()
        banned_found = [b for b in BANNED_SUBSTRINGS if b in low]
        if banned_found:
            print(f"[FAIL] Output contains banned strings: {banned_found}")
            failures += 1
        else:
            print("[PASS] Clean output (no AI leaks or marker tags)")

    print("\n" + "=" * 60)
    if failures == 0:
        print("ALL VERIFICATION CHECKS PASSED (0 failures)")
        print("=" * 60)
        return 0
    else:
        print(f"VERIFICATION FAILED: {failures} failure(s)")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(run_verification())
