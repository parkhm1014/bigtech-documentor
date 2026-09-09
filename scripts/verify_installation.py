#!/usr/bin/env python3
"""
BigTech Retriever - Installation Verification Script
Verifies that all required packages and CUDA are properly installed.
"""

import sys
import subprocess

def print_section(title):
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def check_python():
    print_section("Python Version")
    print(f"Python: {sys.version}")
    major, minor = sys.version_info[:2]
    if major == 3 and minor == 12:
        print("✓ Python 3.12 detected")
        return True
    else:
        print(f"✗ Python 3.12 required, got {major}.{minor}")
        return False

def check_cuda():
    print_section("CUDA")
    try:
        result = subprocess.run(
            ['nvcc', '--version'],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        if '12.8' in result.stdout:
            print("✓ CUDA 12.8 detected")
            return True
        else:
            print("⚠ CUDA version might not be 12.8")
            return True
    except FileNotFoundError:
        print("✗ nvcc not found - CUDA not installed properly")
        return False
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running nvcc: {e}")
        return False

def check_package(package_name, import_name=None, version_attr='__version__'):
    if import_name is None:
        import_name = package_name

    try:
        module = __import__(import_name)
        version = getattr(module, version_attr, 'unknown')
        print(f"✓ {package_name}: {version}")
        return True
    except ImportError:
        print(f"✗ {package_name}: NOT INSTALLED")
        return False
    except Exception as e:
        print(f"⚠ {package_name}: ERROR - {e}")
        return False

def check_pytorch():
    print_section("PyTorch & CUDA")

    try:
        import torch
        print(f"✓ PyTorch: {torch.__version__}")

        cuda_available = torch.cuda.is_available()
        print(f"{'✓' if cuda_available else '✗'} CUDA available: {cuda_available}")

        if cuda_available:
            print(f"  CUDA version (PyTorch): {torch.version.cuda}")
            print(f"  cuDNN version: {torch.backends.cudnn.version()}")
            print(f"  Number of GPUs: {torch.cuda.device_count()}")
            for i in range(torch.cuda.device_count()):
                print(f"  GPU {i}: {torch.cuda.get_device_name(i)}")
                props = torch.cuda.get_device_properties(i)
                print(f"    Memory: {props.total_memory / 1024**3:.1f} GB")
                print(f"    Compute Capability: {props.major}.{props.minor}")

        return cuda_available
    except ImportError:
        print("✗ PyTorch: NOT INSTALLED")
        return False

def check_flash_attention():
    print_section("Flash-Attention")

    try:
        import flash_attn
        print(f"✓ flash-attn: {flash_attn.__version__}")

        # Try to import core components
        try:
            from flash_attn import flash_attn_func
            print("✓ flash_attn_func imported successfully")
        except ImportError as e:
            print(f"⚠ Could not import flash_attn_func: {e}")

        return True
    except ImportError:
        print("✗ flash-attn: NOT INSTALLED")
        return False

def check_deepseek_ocr():
    print_section("DeepSeek-OCR Dependencies")

    results = []
    results.append(check_package('transformers'))
    results.append(check_package('tokenizers'))
    results.append(check_package('einops'))
    results.append(check_package('addict'))
    results.append(check_package('easydict'))

    return all(results)

def check_langchain():
    print_section("LangChain Ecosystem")

    results = []
    results.append(check_package('langchain'))
    results.append(check_package('langchain-core', 'langchain_core'))
    results.append(check_package('langchain-openai', 'langchain_openai'))
    results.append(check_package('langsmith'))

    return all(results)

def check_retrieval():
    print_section("Retrieval & Embedding")

    results = []
    results.append(check_package('faiss', 'faiss'))
    results.append(check_package('sentence-transformers', 'sentence_transformers'))

    try:
        from rank_bm25 import BM25Okapi
        print("✓ rank-bm25: imported successfully")
        results.append(True)
    except ImportError:
        print("✗ rank-bm25: NOT INSTALLED")
        results.append(False)

    return all(results)

def check_scientific():
    print_section("Scientific Computing")

    results = []
    results.append(check_package('numpy'))
    results.append(check_package('pandas'))
    results.append(check_package('scipy'))
    results.append(check_package('scikit-learn', 'sklearn'))

    return all(results)

def check_visualization():
    print_section("Visualization & Image Processing")

    results = []
    results.append(check_package('matplotlib'))
    results.append(check_package('pillow', 'PIL'))

    try:
        import pdf2image
        print(f"✓ pdf2image: {pdf2image.__version__ if hasattr(pdf2image, '__version__') else 'installed'}")
        results.append(True)
    except ImportError:
        print("✗ pdf2image: NOT INSTALLED")
        results.append(False)

    return all(results)

def check_jupyter():
    print_section("Jupyter")

    results = []
    results.append(check_package('ipython', 'IPython'))
    results.append(check_package('ipykernel'))
    results.append(check_package('jupyter-client', 'jupyter_client'))

    return all(results)

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         BigTech Retriever - Installation Verification    ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    checks = []

    checks.append(("Python 3.12", check_python()))
    checks.append(("CUDA Toolkit", check_cuda()))
    checks.append(("PyTorch & GPU", check_pytorch()))
    checks.append(("Flash-Attention", check_flash_attention()))
    checks.append(("DeepSeek-OCR Dependencies", check_deepseek_ocr()))
    checks.append(("LangChain", check_langchain()))
    checks.append(("Retrieval Systems", check_retrieval()))
    checks.append(("Scientific Computing", check_scientific()))
    checks.append(("Visualization", check_visualization()))
    checks.append(("Jupyter", check_jupyter()))

    # Summary
    print_section("Summary")
    passed = sum(1 for _, status in checks if status)
    total = len(checks)

    for name, status in checks:
        symbol = "✓" if status else "✗"
        print(f"{symbol} {name}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All checks passed! Installation is complete.")
        return 0
    else:
        print(f"\n⚠ {total - passed} check(s) failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
