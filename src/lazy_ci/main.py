from lazy_ci.code_quality import run_code_quality
from lazy_ci.ship import ship
import sys


def main():
    if len(sys.argv) == 1:
        print("No command provided, running code quality checks as default")
        if not run_code_quality():
            sys.exit(1)
    elif sys.argv[1] == "code-quality":
        print("Running code quality checks")
        if not run_code_quality():
            sys.exit(1)
    elif sys.argv[1] == "ship":
        print("Shipping code!")
        if not run_code_quality():
            print("Code quality checks failed, not shipping code!!!")
            sys.exit(1)
        else:
            if not ship():
                sys.exit(1)


if __name__ == "__main__":
    main()
