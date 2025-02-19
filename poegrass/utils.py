import datetime
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import re

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

def make_ruby_run(baseText, rubyText, basePoint=11.0, rubyPoint=6.0):
    """ルビ付きのrunを生成する関数"""
    # 本文ランの作成
    base_run = OxmlElement('w:r')
    base_text = OxmlElement('w:t')
    base_text.text = baseText
    base_run.append(base_text)

    # 本文ランのフォントサイズ設定
    base_rpr = OxmlElement('w:rPr')
    base_size = OxmlElement('w:sz')
    base_size.set(qn('w:val'), str(int(basePoint * 2)))  # Wordは半ポイント単位
    base_rpr.append(base_size)
    base_run.insert(0, base_rpr)

    # フリガナランの作成
    ruby_run = OxmlElement('w:r')
    ruby_text = OxmlElement('w:t')
    ruby_text.text = rubyText
    ruby_run.append(ruby_text)

    # フリガナランのフォントサイズ設定
    ruby_rpr = OxmlElement('w:rPr')
    ruby_size = OxmlElement('w:sz')
    ruby_size.set(qn('w:val'), str(int(rubyPoint * 2)))  # Wordは半ポイント単位
    ruby_rpr.append(ruby_size)
    ruby_run.insert(0, ruby_rpr)

    # ルビ構造の作成
    ruby = OxmlElement('w:ruby')  # 本体＆フリガナの入れ物
    rt = OxmlElement('w:rt')  # フリガナの入れ物
    rt.append(ruby_run)
    rubyBase = OxmlElement('w:rubyBase')  # 本体の入れ物
    rubyBase.append(base_run)
    ruby.append(rt)
    ruby.append(rubyBase)

    # 新しいrun要素に追加
    new_run = OxmlElement('w:r')
    new_run.append(ruby)
    return new_run

def make_normal_run(text, point=11.0):
    """通常のrunを生成する関数"""
    # ランの作成
    new_run = OxmlElement('w:r')
    text_element = OxmlElement('w:t')
    text_element.text = text
    new_run.append(text_element)

    # フォントサイズ設定
    rpr = OxmlElement('w:rPr')
    size = OxmlElement('w:sz')
    size.set(qn('w:val'), str(int(point * 2)))  # Wordは半ポイント単位
    rpr.append(size)
    new_run.insert(0, rpr)

    return new_run

def make_ruby_whole_sentence(paragraph,text,basePoint=11.0,rubyPoint=6.0):
    """ルビ付きのrunを生成しparagraphに格納する関数"""
    tagA_pattern = r"<ruby>(.*?)</ruby>" # タグA．baseTextとrubyTextを囲む
    tagB_pattern = r"<rt>(.*?)</rt>" # タグB．rubyTextを囲む
    
    run_list = []
    
    # タグAで分割
    cursor_A = 0
    for match_A in re.finditer(tagA_pattern, text):
        # タグAの前の部分を追加
        run = make_normal_run(text[cursor_A:match_A.start()],point=basePoint)
        run_list.append(run)

        # タグAの中身をタグBで処理
        cursor_B = 0
        group_text = match_A.group(1)
        for match_B in re.finditer(tagB_pattern, group_text):
            baseText = group_text[cursor_B:match_B.start()]
            rubyText = match_B.group(1)
            run = make_ruby_run(baseText, rubyText, basePoint=basePoint, rubyPoint=rubyPoint)
            run_list.append(run)
            cursor_B = match_B.end()
        
        cursor_A = match_A.end()

    # タグAの後の部分を追加
    run_list.append(make_normal_run(text[cursor_A:]))

    for run_item in run_list:
        run = paragraph.add_run()
        run._r.append(run_item)

    return paragraph