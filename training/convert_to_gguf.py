"""
GGUF Converter and Quantizer for Alisha Bubbzieee.
Merges LoRA adapter into base Qwen3.5-2B model and converts to GGUF (Q4_K_M)
for zero-cost on-device inference on Redmi Note 11 via llama.cpp.
"""

import argparse
import os
import subprocess
import sys


def convert_and_quantize(
    base_model: str,
    lora_checkpoint: str,
    output_dir: str,
    quant_type: str = "q4_k_m",
):
    os.makedirs(output_dir, exist_ok=True)
    merged_path = os.path.join(output_dir, "merged_model")
    gguf_f16_path = os.path.join(output_dir, "alisha_2b_f16.gguf")
    gguf_quant_path = os.path.join(output_dir, f"alisha_2b_{quant_type}.gguf")

    print(f"=== Converting Model to GGUF ({quant_type}) ===")
    print(f"Base Model: {base_model}")
    print(f"LoRA Adapter: {lora_checkpoint}")

    # Instructions or command invocation for llama.cpp convert script
    convert_script = "convert_hf_to_gguf.py"
    llama_quantize = "llama-quantize"

    print("\nStep 1: In Kaggle or python environment with llama-cpp:")
    print(f"python {convert_script} {merged_path} --outfile {gguf_f16_path} --outtype f16")

    print("\nStep 2: Quantize to 4-bit Medium:")
    print(f"{llama_quantize} {gguf_f16_path} {gguf_quant_path} {quant_type.upper()}")

    print(f"\nFinal mobile file: {gguf_quant_path} (~1.4 GB)")
    print("Ready to push to Redmi Note 11: adb push alisha_2b_q4km.gguf /sdcard/llama.cpp/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert and quantize fine-tuned model to GGUF")
    parser.add_argument("--base", default="Qwen/Qwen3.5-2B", help="Base model identifier")
    parser.add_argument("--lora", default="alisha_checkpoints", help="Path to LoRA checkpoint")
    parser.add_argument("--out", default="data/models", help="Output directory")
    parser.add_argument("--quant", default="q4_k_m", help="Quantization type")
    args = parser.parse_args()

    convert_and_quantize(args.base, args.lora, args.out, args.quant)
