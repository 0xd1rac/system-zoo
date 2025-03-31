import sys
import getpass
from repl.repl import start 

def main():
    try: 
        username = getpass.getuser()
    except Exception as e:
        print("Error fetching current user: ", e)
        sys.ext(1)

    print(f"Hello {username}! This is the Monkey programming language!")
    print("Feel free to type in commands")

    start()

if __name__ == '__main__':
    main()