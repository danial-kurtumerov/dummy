from os import environ

class CommandLineInterfaceController:

    def __init__(self) -> None:
        pass

    def __call__(self) -> None:
        print("-" * 80)
        print(environ.get("ONBOARD_REPO_MESSAGE", ""))
        print("-" * 80)

if __name__ == "__main__":
    app: CommandLineInterfaceController = CommandLineInterfaceController()
    app()
