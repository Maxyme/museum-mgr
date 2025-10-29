import sqlite3
from wikipediaapi import Wikipedia


def main():

    con = sqlite3.connect("local.db")
    print("Hello from museum-mgr!")

if __name__ == "__main__":
    main()
