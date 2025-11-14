import argparse
from waspai import GetInfo
from waspai import ScanManager
import requests


class Scanner:
    # def __init__(self):  # created for new objects at new depth
    def __init__(self, args):
        self.url = args["url"]
        self.app_type = args["app_type"]
        self.scan_types = args["scan_types"]
        self.scan_map = args["scan_map"]
        self.app_options = args["app_options"]
        self.print_responses = args["print_response"]
        self.session = requests.Session()  # needed only for headers
        self.adaptive_timeout = 20
        self.depth = 0
        self.max_depth = args["max_depth"]

        # these will be filled by getInfo()
        self.driver = None
        self.entry_fields = None
        self.headers = None
        # self.cookies = None

    def getInfo(self) -> None:
        if self.app_type == "auto" or self.app_type == "unknown":
            self.adaptive_timeout, self.app_type, self.driver, self.entry_fields, self.headers = (
                GetInfo.main(self.adaptive_timeout, self.app_options, self.depth, self.scan_map, self.session,
                             self.url))
        else:
            self.adaptive_timeout, self.app_type, self.driver, self.entry_fields, self.headers = (
                GetInfo.main(self.adaptive_timeout, self.app_options, self.depth, self.scan_map, self.session, self.url,
                             self.app_type))

    def manageScans(self) -> None:
        ScanManager.main(self.driver, self.entry_fields, self.headers, self.scan_types)


def clean_args(raw: argparse.Namespace) -> dict[str: any]:
    short_flag_map: dict[str, str] = {
        "b": "broken_access_control",  # b = Broken access
        "c": "cryptographic_failure",  # c = Cryptographic
        "i": "injection",  # i = injection
        "d": "insecure_design",  # d = Design00
        "m": "security_misconfiguration",  # m = misconfig
        "v": "vulnerable_and_outdated_components",  # v = vulnerable components
        "a": "identification_and_authentication_failures",  # a = auth / identification
        "s": "software_and_data_integrity_failures",  # S = Software integrity
        "l": "security_logging_and_monitoring_failures",  # l = logging
        "r": "server_side_requests_forgery"  # r = request forgery (SSRF)
    }
    scan_types: dict[str, int] = {  # when scan is done set value to 1
        "b": 0, "c": 0, "i": 0, "d": 0, "m": 0, "v": 0, "a": 0, "s": 0, "l": 0, "r": 0
    }  # if scan shouldn't be done set value to 1 before starting
    app_options = [
        "auto", "static", "dynamic", "php", "laravel", "django", "flask", "aspnet", "dotnet-blazor", "ruby-on-rails",
        "java-spring", "react", "nextjs", "vue", "nuxt", "angular", "svelte", "wordpress", "drupal", "joomla",
        "magento", "shopify", "api", "unknown"
    ]

    if raw.scan is not None:
        raw.scan = raw.scan.split(",")
        for i in scan_types:
            if i not in raw.scan:
                del short_flag_map[i]
                scan_types[i] = 1

    # printing errors if something isn't in the above list or dict
    if raw.app_type not in app_options:
        raise argparse.ArgumentTypeError(f"Invalid App Type given, please select a valid option\n{app_options}.")

    if raw.url is None:
        raise argparse.ArgumentTypeError("No URL given.")
    elif not raw.url.startswith(("https://", "http://")):
        raw.url = ("https://" + raw.url).strip().lower()

    return {
        "app_options": app_options,
        "app_type": raw.app_type,
        "max_depth": raw.max_depth,
        "print_response": raw.print_response,
        "scan_map": short_flag_map,
        "scan_types": scan_types,
        "url": raw.url,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='waspai', description='An AI-integrated Web Scanner')
    parser.add_argument("url", help="Target web app URL (e.g., http://localhost:3030)")
    parser.add_argument(
        '-t', '--app-type',
        default="auto",
        help=f"Specify app type (default: auto-detect)\n"
    )
    parser.add_argument('-scan', '--scan',
                        dest='scan',
                        type=str,
                        help="Comma-separated short letters of scans to run, ex. 'i' or 'i,b'. If not, runs all scans.")
    parser.add_argument('-pr', '--print-response',
                        action='store_true',
                        help="Print response for AI explanation")
    parser.add_argument('-depth', '--depth',
                        help='Set a max depth for scanner (# of redirects to follow)',
                        type=int,
                        default=3,
                        dest="max_depth")

    return parser


def runner(scanner) -> str:
    results = ""

    scanner.getInfo()

    # print(scanner.scan_type)
    ''' FOR TESTING PURPOSES TO SEE THE FIELDS UNCOMMENT THIS TO PRINT RESULTS OF SCAN* ************** '''
    for i in scanner.entry_fields:
        print(i)
    ''' '''
    scanner.manageScans()

    return results


def main() -> int:
    parser = build_parser()
    args_ns = parser.parse_args()
    try:
        args = clean_args(args_ns)
    except argparse.ArgumentTypeError as e:
        parser.error(str(e))
        return 0

    scanner = Scanner(args)  # create the Scanner object
    results = runner(scanner)  # results will be the final scoring / feedback

    return 1


if __name__ == "__main__":
    main()
