import boilerutils
import builder
import sys
import os

def handle_test_args(args):
    for arg in range(len(args)):
        if args[arg] == "-t" or args[arg] == "--test":
            boilerutils.DEP_DIR = "dependencies"
            boilerutils.CONF_DIR = "config"
        if args[arg] == "-d" or args[arg] == "--dependencies":
            if arg + 1 < len(args):
                if os.path.exists(args[arg + 1]):
                    boilerutils.DEP_DIR = args[arg + 1]
                else:
                    print("Provided directory for dependencies does not exist.")
            else:
                print("No directory provided for dependencies.")
        if args[arg] == "-c" or args[arg] == "--config":
            if arg + 1 < len(args):
                # check if the directory exists
                if os.path.exists(args[arg + 1]):
                    boilerutils.CONF_DIR = args[arg + 1]
                else:
                    print("Provided directory for config does not exist.")
            else:
                print("No directory provided for config.")

def main():
    handle_test_args(sys.argv)

    test = builder.Builder("x86_64-elf")
    test.load_build()
    test.download_source()
    test.create_build_script()
    test.run_build_script()

if __name__ == "__main__":
    main()
