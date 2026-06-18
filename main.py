import sys
import os

# Ensure project root is on sys.path so relative imports work when running as script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import ASMRifyApp


def main():
    app = ASMRifyApp()
    app.run()


if __name__ == "__main__":
    main()
