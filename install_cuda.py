"""
Installs cuda + transcibe-anything
"""

import argparse
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
API_PY = os.path.join(HERE, "api.py")

# Set the versions
TENSOR_VERSION = "1.12.1"
CUDA_VERSION = "cu116"
TENSOR_CUDA_VERSION = f"{TENSOR_VERSION}+{CUDA_VERSION}"
EXTRA_INDEX_URL = "https://download.pytorch.org/whl/cu116"


argparser = argparse.ArgumentParser()
argparser.add_argument("--display-cuda-version", default=CUDA_VERSION, help="displays cuda version")
argparser.add_argument(
    "--force", action="store_true", help="Force install and ignore missing nvida drivers"
)
args = argparser.parse_args()

HAS_NVIDIA: bool = shutil.which("nvidia-smi") is not None

if not HAS_NVIDIA and not args.force:
    print("No nvidia-smi detected, skipping cuda install")
    sys.exit(1)

# Get the stdout from pip list
pip_list_stdout = subprocess.run(
    ["pip", "list", "--format", "json"], check=True, capture_output=True, universal_newlines=True
).stdout

# Delete the torch package if it doesn't have the cuda version
if args.force:
    subprocess.run(["pip", "uninstall", "-y", "torch"], check=True)
    subprocess.run(["pip", "cache", "purge"], check=True)
else:
    if TENSOR_CUDA_VERSION not in pip_list_stdout:
        print(f"The substring '${TENSOR_CUDA_VERSION}' does not exist in the string.")
        subprocess.run(["pip", "uninstall", "-y", "torch"], check=True)
        print("Purging pip cache to remove any torch packages that are cpu only")
        subprocess.run(["pip", "cache", "purge"], check=True)
    else:
        print(f"Tensorflow {TENSOR_CUDA_VERSION} is currently installed")

# Install torch with cuda
print("Installing torch+cuda")
subprocess.run(
    [
        "pip",
        "install",
        f"torch=={TENSOR_VERSION}",
        "--extra-index-url",
        EXTRA_INDEX_URL,
    ],
    check=True,
)


def use_local_install() -> bool:
    """Prompts the user for the install path, if we detect that this is in a github action"""

    if os.path.exists(API_PY):
        use_local = input("Use local install? [y/n] ").lower() == "y"
        if use_local:
            return True
    return False


USE_LOCAL_INSTALL = use_local_install()
if USE_LOCAL_INSTALL:
    install_cmd = ["pip", "install", "-e", "."]
else:
    install_cmd = ["pip", "install", "transcribe-anything"]

# Install transcribe_anything
print("Install transcribe_anything:\n", " ".join(install_cmd))
subprocess.run(install_cmd, check=True)

print("\ntranscribe audio is installed, run it with\n  transcribe_audio <URL OR FILE>")
