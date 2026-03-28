from os import environ


def main():
    print("-" * 80)

    for name, value in environ.items():
        print(f"{name}: {value}")
    
    print("-" * 80)


if __name__ == "__main__":
    main()
