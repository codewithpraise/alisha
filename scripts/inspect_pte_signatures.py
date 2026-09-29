import os
import sys

def main():
    try:
        from executorch.runtime import Runtime
    except Exception as e:
        print(f"Failed to import executorch: {e}")
        return

    runtime = Runtime.get()
    pte_files = [
        "speaker_encoder_int8.pte",
        "code_predictor_int8.pte",
        "vocoder_int8.pte",
        "talker_int8.pte",
    ]

    for pte in pte_files:
        if not os.path.exists(pte):
            print(f"[MISSING] {pte}")
            continue

        size_mb = os.path.getsize(pte) / (1024 * 1024)
        print(f"\n=======================================================")
        print(f"FILE: {pte} ({size_mb:.2f} MB)")
        print(f"=======================================================")

        try:
            prog = runtime.load_program(pte)
            methods = sorted(list(prog.method_names))
            print(f"Methods: {methods}")

            for m in methods:
                meta = prog.metadata(m)
                num_in = meta.num_inputs()
                num_out = meta.num_outputs()
                print(f"--- Method '{m}' ---")
                print(f"Inputs count: {num_in}")
                for i in range(num_in):
                    try:
                        tinfo = meta.input_tensor_meta(i)
                        attrs = [a for a in dir(tinfo) if not a.startswith('__')]
                        if i == 0:
                            print(f"  tinfo attrs: {attrs}")
                        dtype_val = getattr(tinfo, 'dtype', getattr(tinfo, 'scalar_type', None))
                        print(f"  in[{i}]: sizes={tinfo.sizes()} dtype={dtype_val}")
                    except Exception as e:
                        print(f"  in[{i}]: {e}")

                print(f"Outputs count: {num_out}")
                for i in range(num_out):
                    try:
                        tinfo = meta.output_tensor_meta(i)
                        dtype_val = getattr(tinfo, 'dtype', getattr(tinfo, 'scalar_type', None))
                        print(f"  out[{i}]: sizes={tinfo.sizes()} dtype={dtype_val}")
                    except Exception as e:
                        print(f"  out[{i}]: {e}")

        except Exception as e:
            print(f"Error inspecting {pte}: {e}")

if __name__ == "__main__":
    main()
