from pystock.crawler.crawler import Crawler


class IPOListCrawler(Crawler):
    """
    指定した年にIPOした企業名と銘柄コードを取得する
    """

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def crawl(self) -> dict:
        """
        urlをcrawlし、取得した結果を返す関数
        """
        res = self.get_beautifulsoup_result(target_url=self.url)
        table_content = res.find("div", {"class": "tablewrap"})
        table_thead = table_content.find("thead")
        # headの取得
        table_head_list = []
        for th in table_thead.find_all("th"):
            table_head_list.append(th.get_text())

        # bodyの取得
        table_tbody = table_content.find("tbody")
        whole_result = {}
        for idx, tr in enumerate(table_tbody.find_all("tr")):
            table_body_dict = {}
            for header, td in zip(table_head_list, tr.find_all("td")):
                table_body_dict[header] = td.get_text().replace("\n", "")
            whole_result[idx] = table_body_dict
        return whole_result
