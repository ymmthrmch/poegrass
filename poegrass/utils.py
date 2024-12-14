import datetime

def japanese_strftime(date,format_str):

    if not isinstance(date,datetime.datetime):
        raise ValueError("引数にはdatetimeオブジェクトを渡してください")

    japanese_Weekdays = ["日曜日","月曜日","火曜日","水曜日","木曜日","金曜日","土曜日"]
    japanese_weekdays = ["日","月","火","水","木","金","土"]
    japanese_Weekday = japanese_Weekdays[date.weekday()]
    japanese_weekday = japanese_weekdays[date.weekday()]
    format_str = format_str.replace("%A", japanese_Weekday)
    format_str = format_str.replace("%a", japanese_weekday)

    return date.strftime(format_str)
    