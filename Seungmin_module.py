import urllib.request
from bs4 import BeautifulSoup


def _crawl_opgg_keywords(text):
    if text == 'Default Fallback Intent':
        return ''
    # 여기에 함수를 구현해봅시다.
    keywords = {}

    sourcecode1 = urllib.request.urlopen('http://www.op.gg/champion/ajax/statistics/trendChampionList/type=winratio&').read()
    soup1 = BeautifulSoup(sourcecode1, "html.parser")
    sourcecode2 = urllib.request.urlopen('http://www.op.gg/champion/ajax/statistics/trendChampionList/type=banratio&').read()
    soup2 = BeautifulSoup(sourcecode2, "html.parser")

    winpick_champ = [i.get_text() for i in soup1.find_all("div", class_="champion-index-table__name")]
    winpick_champ = winpick_champ[:142]
    winratio = [i.get_text() for i in soup1.find_all("td", class_="champion-index-table__cell champion-index-table__cell--value champion-index-table__cell--blue")]
    winratio = winratio[:142]
    pickratio = [i.get_text() for i in soup1.find_all("td", class_ = "champion-index-table__cell champion-index-table__cell--value")]
    pickratio = pickratio[:142]

    ban_champ = [i.get_text() for i in soup2.find_all("div", class_="champion-index-table__name")]
    ban_champ = ban_champ[:142]
    banratio = [i.get_text() for i in soup2.find_all("td", class_ = "champion-index-table__cell champion-index-table__cell--value champion-index-table__cell--blue")]
    banratio = banratio[:142]

    for i in range(len(winpick_champ)):
        if not winpick_champ[i] in keywords:
            keywords[winpick_champ[i]] = [winratio[i], pickratio[i]]

    for i in range(len(ban_champ)):
        if ban_champ[i] in keywords:
            keywords[ban_champ[i]].append(banratio[i])

    for i in range(len(keywords)):
        keywords[winpick_champ[i]][0], keywords[winpick_champ[i]][2] = keywords[winpick_champ[i]][2], keywords[winpick_champ[i]][0]

'''
    for data in soup1.find_all("div", class_="champion-index-table__name"):
        if not data.get_text() in keywords:
    for data in soup.find_all("p", class_="artist"):
        if not data.get_text() in keywords:
            if len(singer) >= 10:
                break
            singer.append(data.get_text().strip('\n'))
    for i in range(len(titles)):
        keywords.append(str(i + 1) + "위: " + titles[i] + "/" + singer[i])
    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(keywords)
'''
a = _crawl_opgg_keywords('aa')