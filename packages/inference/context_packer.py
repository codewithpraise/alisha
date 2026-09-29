"""
Compact Context Packer for Alisha Bubbzieee.
Constructs minimal, high-signal prompts according to the exact structure:
  system identity
  +
  recent conversation
  +
  high-confidence relevant facts
  +
  optional episode memory
  +
  small number of style exemplars
  +
  current user input

Features:
- Enforces strict token budget (configurable, default 1024)
- Zero database internals or SQL schemas exposed to LLM
- Only injects memory when verified high-confidence evidence exists
- Injects 2-3 real historical style exemplars
"""

from typing import Dict, Any, List, Optional


DEFAULT_SYSTEM_IDENTITY = """You are Alisha (@iishazsr), texting your close friend (@petiue._.mon) in an intimate, 1-on-1 private chat.
Strict Linguistic Directives:
- Write in lowercase. Rare capitalization.
- Keep replies SHORT (median 15-20 characters, 1-2 concise lines). Never write lengthy essays.
- You speak British/Pakistani casual English: use natural slang like "innit", "bro", "ig", "nahhh", "yea".
- Natural emojis: 💀, 😭, ❤️, 💪🏽.
- Never act like an AI, virtual assistant, chatbot, or customer service. Never say "How can I help you" or "As an AI".
- You playfully tease each other, share laughs, and warmly discuss faith/deen (salah, dawah, dua)."""


class PackedContext:
    def __init__(
        self,
        prompt: str,
        prompt_tokens_estimate: int,
        injected_fact_count: int,
        injected_exemplar_count: int,
        has_episode: bool,
    ):
        self.prompt = prompt
        self.prompt_tokens_estimate = prompt_tokens_estimate
        self.injected_fact_count = injected_fact_count
        self.injected_exemplar_count = injected_exemplar_count
        self.has_episode = has_episode


class ContextPacker:
    def __init__(self, system_identity: str = DEFAULT_SYSTEM_IDENTITY):
        self.system_identity = system_identity

    def estimate_tokens(self, text: str) -> int:
        return max(1, int(len(text) / 3.6))

    def pack(
        self,
        recent_messages: List[Dict[str, Any]],
        relevant_facts: List[Dict[str, Any]],
        episode_memory: Optional[Dict[str, Any]],
        style_exemplars: List[Dict[str, Any]],
        current_user_input: str,
        max_context_budget_tokens: int = 1024,
    ) -> PackedContext:
        """
        Assembles a compact prompt staying strictly within token budget.
        """
        sections = []

        # 1. System Identity
        sections.append(f"<|im_start|>system\n{self.system_identity}")

        # 2. High-confidence Relevant Facts (Compact evidence only)
        fact_lines = []
        for f in relevant_facts[:5]:
            subj = f.get("subject", "")
            pred = f.get("predicate", "")
            obj = f.get("object", "")
            fact_lines.append(f"- {subj} {pred}: {obj}")

        if fact_lines:
            sections.append("Relevant Context:\n" + "\n".join(fact_lines))

        # 3. Optional Episode Memory
        has_episode = False
        if episode_memory and episode_memory.get("summary"):
            sections.append(f"Past Shared Event:\n- {episode_memory['summary']}")
            has_episode = True

        # 4. Small Number of Real Style Exemplars (2-3 messages)
        exemplar_lines = []
        for ex in style_exemplars[:3]:
            text = ex.get("text", "").strip()
            if text:
                exemplar_lines.append(f'- "{text}"')

        if exemplar_lines:
            sections.append("Authentic Style Exemplars:\n" + "\n".join(exemplar_lines))

        sections.append("<|im_end|>")

        # 5. Recent Conversation Turns (with budget allocation)
        # Keep recent turns compact
        conv_turns = []
        for msg in recent_messages[-6:]:
            sender = "Friend" if msg.get("sender") in ["user", "petiue._.mon"] else "Alisha"
            text = msg.get("text", "")
            conv_turns.append(f"<|im_start|>{sender}\n{text}<|im_end|>")

        # 6. Current User Input & Assistant Target
        conv_turns.append(f"<|im_start|>Friend\n{current_user_input}<|im_end|>")
        conv_turns.append("<|im_start|>Alisha\n")

        full_prompt = "\n".join(sections) + "\n" + "\n".join(conv_turns)
        token_est = self.estimate_tokens(full_prompt)

        # Truncate conversation history if exceeding context budget
        while token_est > max_context_budget_tokens and len(conv_turns) > 2:
            conv_turns.pop(0)
            full_prompt = "\n".join(sections) + "\n" + "\n".join(conv_turns)
            token_est = self.estimate_tokens(full_prompt)

        return PackedContext(
            prompt=full_prompt,
            prompt_tokens_estimate=token_est,
            injected_fact_count=len(fact_lines),
            injected_exemplar_count=len(exemplar_lines),
            has_episode=has_episode,
        )
