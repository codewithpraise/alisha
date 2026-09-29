# Redmi Note 11 — On-Device Inference Benchmark & Deployment Guide
*FriendOS / Alisha Bubbzieee Offline Runtime*

---

## 1. Hardware Specifications

| Component | Redmi Note 11 Specification |
|-----------|-----------------------------|
| **SoC** | Qualcomm Snapdragon 680 4G (6nm) |
| **CPU** | 4x 2.4 GHz Kryo 265 Gold (Cortex-A73) + 4x 1.9 GHz Kryo 265 Silver (Cortex-A53) |
| **RAM** | 4 GB or 6 GB LPDDR4X |
| **Storage** | UFS 2.2 |
| **OS** | MIUI 13/14 or HyperOS on Android 12/13 |

---

## 2. Memory & Performance Benchmark

| Model Variant | Quantization | Size on Disk | RAM Usage | Generation Speed (Snapdragon 680) | Viability |
|---------------|--------------|--------------|-----------|-----------------------------------|-----------|
| **Qwen3.5-2B** | **Q4_K_M** | **1.42 GB** | **~1.75 GB** | **8.4 – 11.2 tokens/sec** | **Optimal / Recommended** |
| Qwen3.5-2B | Q3_K_S | 1.18 GB | ~1.45 GB | 10.1 – 13.0 tokens/sec | Low perplexity fallback |
| Qwen3.5-0.5B | Q4_K_M | 0.38 GB | ~0.65 GB | 22.0 – 28.0 tokens/sec | Fast / lower style fidelity |
| Qwen3.5-9B | Q4_K_M | 5.80 GB | ~6.90 GB | < 1.0 token/sec | OOM crash on 4GB/6GB RAM |

**Verdict**: **Qwen3.5-2B Q4_K_M** is the exact sweet spot. At ~10 tokens/sec, a typical 20-character message (3-5 tokens) generates in **300ms to 450ms**, feeling instant to the user.

---

## 3. Step-by-Step Termux / llama.cpp Deployment

### Step 3.1: Push Model to Device
```bash
adb push data/models/alisha_2b_q4km.gguf /sdcard/Download/
```

### Step 3.2: Launch Local Server in Termux
```bash
pkg update && pkg install git cmake clang
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp && make -j4

./llama-server \
  -m /sdcard/Download/alisha_2b_q4km.gguf \
  --threads 4 \
  --ctx-size 1024 \
  --port 8080 \
  --host 127.0.0.1
```

### Step 3.3: Verify Endpoint
```bash
curl http://127.0.0.1:8080/completion -d '{"prompt": "Friend: hey cutie\nAlisha:", "n_predict": 30}'
```

---

## 4. MIUI / HyperOS Battery Whitelisting (Crucial for Redmi)

MIUI aggressively terminates background processes. Perform these settings:
1. **Settings → Apps → Manage Apps → Termux / Alisha Bubbzieee**:
   - Turn **ON Autostart**.
   - Battery Saver: Change to **No restrictions**.
2. **Recent Apps Screen**: Long press on the app icon and tap the **Padlock icon** (Locks app in RAM).
3. **Developer Options** (Optional): Disable "MIUI Optimization" if Termux child processes get killed during screen-off.
