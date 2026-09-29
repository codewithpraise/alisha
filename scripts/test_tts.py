import os
import sys
import subprocess
import time

def test_sapi_tts(text: str, output_wav: str) -> bool:
    """Uses Windows built-in SpeechSynthesizer to generate real WAV audio."""
    ps_script = f'''
    Add-Type -AssemblyName System.Speech
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $voices = $synth.GetInstalledVoices()
    foreach ($v in $voices) {{
        if ($v.VoiceInfo.Gender -eq "Female") {{
            $synth.SelectVoice($v.VoiceInfo.Name)
            break
        }}
    }}
    $synth.SetOutputToWaveFile("{output_wav}")
    $synth.Speak("{text}")
    $synth.Dispose()
    '''
    try:
        res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True, timeout=5)
        if os.path.exists(output_wav) and os.path.getsize(output_wav) > 100:
            print(f"[SAPI TTS Success] Generated {output_wav} ({os.path.getsize(output_wav)} bytes)")
            return True
        else:
            print(f"[SAPI TTS Notice] Output file missing or empty: {res.stderr}")
            return False
    except Exception as e:
        print(f"[SAPI TTS Error] {e}")
        return False

if __name__ == "__main__":
    out = os.path.abspath("test_sapi.wav")
    success = test_sapi_tts("hey, what are you doing right now?", out)
    if os.path.exists(out):
        print("SAPI Test File Verified:", os.path.getsize(out))
