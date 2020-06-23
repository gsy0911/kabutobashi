from datetime import datetime, timedelta
import jpholiday


def get_past_n_days(current_date: str, n: int = 60) -> list:
    """
    土日と祝日を考慮したn営業日前までの日付のリストを返す関数

    Args:
        current_date: n日前を計算する起点となる日
        n: n日前

    Returns:
        date list, ex ["%Y-%m-%d", "%Y-%m-%d", "%Y-%m-%d", ...]
    """
    end_date = datetime.strptime(current_date, "%Y-%m-%d")
    # 2倍しているのは土日や祝日が排除されるため
    back_n_days = n * 2
    date_candidate = [end_date - timedelta(days=d) for d in range(back_n_days)]
    # 土日を除く
    filter_weekend = [d for d in date_candidate if d.weekday() < 5]
    # 祝日を除く
    filter_holiday = [d for d in filter_weekend if not jpholiday.is_holiday(d)]
    # 文字列に日付を変えてreturn
    return list(map(lambda x: x.strftime("%Y-%m-%d"), filter_holiday[:n]))
