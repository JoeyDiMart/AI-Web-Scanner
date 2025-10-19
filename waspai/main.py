import argparse
from waspai import GetInfo
import requests

APP_TYPES = ["auto", "php", "node", "django", "wordpress", "dotnet", "unknown"]
SCAN_TYPES: dict[str, int] = {
    "b": 0,
    "c": 0,
    "i": 0,
    "d": 0,  # when scan is done set value to 1
    "m": 0,  # if scan shouldn't be done set value to 1 before starting
    "v": 0,
    "a": 0,
    "s": 0,
    "l": 0,
    "r": 0
}
SHORT_FLAG_MAP: dict[str, str] = {
    "b": "broken_access_control",  # b = Broken access
    "c": "cryptographic_failure",  # c = Cryptographic
    "i": "injection",  # i = injection
    "d": "insecure_design",  # d = Design
    "m": "security_misconfiguration",  # m = misconfig
    "v": "vulnerable_and_outdated_components",  # v = vulnerable components
    "a": "identification_and_authentication_failures",  # a = auth / identification
    "s": "software_and_data_integrity_failures",  # S = Software integrity
    "l": "security_logging_and_monitoring_failures",  # l = logging
    "r": "server_side_requests_forgery"  # r = request forgery (SSRF)
}


class Scanner:

    def __init__(self, args):
        self.args = args
        self.url = args["url"]
        self.app_type = args["app_type"]
        self.scan_type = args["scan_type"]
        self.print_responses = args["print_responses"]
        self.session = requests.Session()  # created session object for the cookies

        # these will be filled by getInfo()
        self.input_fields = None
        self.headers = None
        self.cookies = None

    def getInfo(self) -> None:
        self.input_fields, self.headers, self.cookies = GetInfo.main(self.url, self.session)


def clean_args(raw: argparse.Namespace) -> dict[str: any]:
    global SCAN_TYPES
    if raw.url is None:
        raise argparse.ArgumentTypeError("No URL given.")
    if raw.app_type not in APP_TYPES:
        raise argparse.ArgumentTypeError(f"Invalid App Type given, please select a valid option\n{APP_TYPES}.")
    if raw.scan is not None:
        for j in SCAN_TYPES:
            SCAN_TYPES[j] = 1
        scan = set(s.strip() for s in raw.scan.split(',') if s.strip())
        for i in scan:
            if i not in SCAN_TYPES:
                raise argparse.ArgumentTypeError(f"Argument '{i}' is not a valid option.\n{SHORT_FLAG_MAP}")
            else:
                SCAN_TYPES[i] = 0
    if raw.print_responses is None:
        raw.print_responses = False
    else:
        raw.print_responses = True

    return {
        "url": raw.url,
        "app_type": raw.app_type,
        "scan_type": raw.scan,
        "print_responses": raw.print_responses
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='waspai', description='An AI-integrated Web Scanner')
    parser.add_argument("url", help="Target web app URL (e.g., http://localhost:3030)")
    parser.add_argument(
        '-t', '--app-type',
        default="auto",
        help=f"Specify app type (default: auto-detect)\n{APP_TYPES}"
    )
    parser.add_argument('-scan', '--scan',
                        dest='scan',
                        help="Comma-separated short letters of scans to run, ex. 'i' or 'i,b'. If not, runs all scans.")
    parser.add_argument('-pr', '--print-responses', help="Print all JSON responses")

    return parser


def main() -> int:
    parser = build_parser()
    args_ns = parser.parse_args()
    try:
        args = clean_args(args_ns)
    except argparse.ArgumentTypeError as e:
        parser.error(str(e))
        return 0

    scanner = Scanner(args)
    scanner.getInfo()

    return 1


if __name__ == "__main__":
    main()
