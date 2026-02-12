import PyInstaller.__main__
import shutil
import os
import sys


def build():
    print("Building Gmail Cleaner...")

    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")

    # Fix for macOS where /usr/local/bin/arch might shadow /usr/bin/arch
    # PyInstaller relies on /usr/bin/arch behavior
    if sys.platform == "darwin":
        os.environ["PATH"] = "/usr/bin:" + os.environ.get("PATH", "")

    PyInstaller.__main__.run(["gmail-cleaner.spec", "--noconfirm", "--clean"])

    print("Build complete! Executable is in dist/gmail-cleaner/")


if __name__ == "__main__":
    build()
