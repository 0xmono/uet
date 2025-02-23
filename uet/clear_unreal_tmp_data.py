import os
import re
import sys
import shutil

PARTH_TO_SCRIPT = os.path.realpath(__file__)
WORKING_DIRECTORY = os.path.dirname(PARTH_TO_SCRIPT)

def clear_folders(*args):
    # Use modern f-strings and type hints
    words: list[str] = list(args) or ['Binaries', 'Intermediate', 'Saved']
    
    # Use list comprehension for validation
    if not all(isinstance(word, str) for word in words):
        raise TypeError("All arguments must be strings")

    print(f'Going to delete {", ".join(words)} in {WORKING_DIRECTORY}')
    pattern = f'.+/({"|".join(words)})$'
    matcher = re.compile(pattern)

    # Use list comprehension for better readability
    matching_dirs = [
        root for root, _, _ in os.walk(WORKING_DIRECTORY)
        if matcher.match(root)
    ]

    print(f'{"No" if not matching_dirs else len(matching_dirs)} matching folders found')

    for root in matching_dirs:
        print(f'Deleting {root}')
        shutil.rmtree(root, True)

def main():
    print(f'Running {PARTH_TO_SCRIPT}')
    print(f'Working directory: {WORKING_DIRECTORY}')
    
    if len(sys.argv) <= 1:
        print("Script must be launched with command line arguments. Aborting.")
        return

    func_name = sys.argv[1]
    func_args = sys.argv[2:]
    
    try:
        func = globals()[func_name]
        func(*func_args)
        print('Job finished!')
    except KeyError:
        print(f"Function '{func_name}' not found")
    except Exception as e:
        print(f"Error executing {func_name}: {e}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nInterrupted by user')
        sys.exit(0)
