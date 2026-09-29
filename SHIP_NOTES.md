# Alisha — Ship Notes (post controller tuning)

## Frozen at
- MODEL        : alisha-v5-Q6_K.gguf (2.45 GB)
- USE_GRAMMAR  : True
- N_SAMPLES    : 1
- Sampler      : --temp 0.75 --dynatemp-range 0.15 --min-p 0.05
                 --top-p 0.90 --top-k 40 --repeat-penalty 1.05
                 -n 60 -no-cnv --no-warmup -t 4 -ngl 0
- Grammar      : alisha.gbnf

## Decisions made — do not re-litigate
- N=2 reranking tested and REGRESSED. Stay at N=1.
- Q6_K beats Q4_K_M meaningfully on free-form probes. Ship Q6_K.
- GBNF grammar kills ~50% of base-Qwen "asks back" leaks. Keep it.
- Retrieval was tested twice in prior sessions, was a wash. DO NOT re-add.
- Short-circuit layer (GREET + FROZEN) is deterministic and handoff-sanctioned.

## _norm() spec
lowercase -> strip ' and ’ -> strip [^\w\s] -> collapse whitespace.

## Verified outcomes
- Frozen eval (8 prompts) : deterministic 3/3 via short-circuit.
- Free-form probe set     : ~11/15 on-tone, drift is in-character, no AI leaks.

## What NOT to touch
- Do not retrain. Do not change hyperparameters.
- Do not use alisha_v5_merged_16bit dir (truncated).
- Do not pass raw text to llama-cli; always use chat markers.
- Do not trust ggerganov/llama.cpp release URLs (broken since b11027).
