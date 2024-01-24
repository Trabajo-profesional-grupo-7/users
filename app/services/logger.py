class Logger():
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[34m'
    END = '\033[0m'

    def err(self, msg: str):
        print(f"{Logger.RED}[ERROR]{Logger.END} - {msg}")

    def debug(self, msg: str):
        print(f"{Logger.GREEN}[DEBUG]{Logger.END} - {msg}")

    def info(self, msg: str):
        print(f"{Logger.BLUE}[INFO]{Logger.END} - {msg}")
