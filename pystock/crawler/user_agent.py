import random


class UserAgent:

    @staticmethod
    def get_user_agent() -> str:
        browser_idx = random.randint(0, 1)
        if browser_idx == 0:
            return Chrome.get_user_agent()
        elif browser_idx == 1:
            return Firefox.get_user_agent()
        else:
            return ""

    @staticmethod
    def get_user_agent_header() -> dict:
        return {"User-Agent": UserAgent.get_user_agent()}


class Chrome:
    mac_chrome_format = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version} Safari/537.36"
    windows_chrome_format = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_version}"

    os_format_list = [
        mac_chrome_format,
        windows_chrome_format
    ]

    os_size = len(os_format_list) - 1

    version_list = [
        "77.0.3865",
        "78.0.3904",
        "79.0.3945.130",
        "80.0.3987",
        "81.0.4044"
    ]

    version_size = len(version_list) - 1

    @staticmethod
    def get_user_agent() -> str:
        os_idx = random.randint(0, Chrome.os_size)
        chrome_format = Chrome.os_format_list[os_idx]
        version_idx = random.randint(0, Chrome.version_size)
        version = Chrome.version_list[version_idx]
        return chrome_format.format(chrome_version=version)


class Firefox:
    # Firefox
    mac_firefox_format = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:62.0) Gecko/20100101 Firefox/{firefox_version}"
    windows_firefox_format = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/{firefox_version}"

    os_format_list = [
        mac_firefox_format,
        windows_firefox_format
    ]

    os_size = len(os_format_list) - 1

    version_list = [
        "68.4.2",
        "72.0.2",
        "73.0",
        "74.0"
    ]

    version_size = len(version_list) - 1

    @staticmethod
    def get_user_agent() -> str:
        os_idx = random.randint(0, Firefox.os_size)
        chrome_format = Firefox.os_format_list[os_idx]
        version_idx = random.randint(0, Firefox.version_size)
        version = Firefox.version_list[version_idx]
        return chrome_format.format(firefox_version=version)
