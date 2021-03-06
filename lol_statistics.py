import json
import urllib.request
import requests

from slacker import Slacker
from bs4 import BeautifulSoup
from slackclient import SlackClient
from flask import Flask, request, make_response, render_template, jsonify
from operator import itemgetter
from math import floor

app = Flask(__name__)

slack_token = "xoxb-503818135714-507351131987-KC8Tcl563Z9NuL505vFJK4bF"
slack_client_id = "503818135714.507348823507"
slack_client_secret = "8194f60277b7af2f46584293915e356b"
slack_verification = "hgtt6xtPYcb4Oq5TzDPhYFOr"
sc = SlackClient(slack_token)
slack = Slacker(slack_token)

'''
챔피언을 추천해달라는 명령어가 입력되어 추천 인텐트가 실행되었을 때 호출되는 함수로
챔피언의 승률과 픽률을 기반으로 추천 지수를 계산하여 추천 지수가 높은 10개 챔피언의 목록을
반환하는 함수
'''
def crawl_opgg_recommend(intent):
    # 엉뚱한 명령어에 대한 호출이 발생되면 아무것도 반환하지 않는다.
    if intent == 'Default Fallback Intent':
        return ''

    keywords = []
    statistics = []

    # 승/픽률 페이지에서 데이터를 받아온다.
    sourcecode1 = urllib.request.urlopen(
        'http://www.op.gg/champion/ajax/statistics/trendChampionList/type=winratio&').read()
    soup1 = BeautifulSoup(sourcecode1, "html.parser")

    # 승/픽률을 기반으로 한 챔피언 목록과 승/픽률을 각 리스트에 받아온다.
    # 이때, 페이지 내에 같은 유형의 데이터가 반복되므로 정해진 챔피언의 개수만큼 리스트들을 슬라이싱 한다.
    winpick_champ = [i.get_text() for i in soup1.find_all("div", class_="champion-index-table__name")]
    winpick_champ = winpick_champ[:142]
    winratio = [i.get_text() for i in soup1.find_all("td",
                                                     class_="champion-index-table__cell champion-index-table__cell--value champion-index-table__cell--blue")]
    winratio = winratio[:142]
    pickratio = [i.get_text() for i in
                 soup1.find_all("td", class_="champion-index-table__cell champion-index-table__cell--value")]
    pickratio = pickratio[:142]

    # 챔피언의 이름과 승률, 픽률을 이용한 추천 지수를 계산 한다. 이때, 자료는 스트링 형태의 데이터로 저장되어 있으므로
    # 뒤에 붙어있는 %를 없애준 후 float 형태로 캐스팅 해준다.
    # 계산된 추천 지수를 이용하여 (챔피언 이름, 추천 지수) 형태의 튜플 자료형으로 저장한다.
    # 결과를 추천 지수별로 정렬하기 위해 튜플의 인자 중 2번째 인자를 이용한다.
    # 정렬된 결과 중 상위 10개의 결과들만 키워드 리스트에 형식을 맞추어 저장해준다.
    # 가장 추천 지수가 높은 챔피언의 초상화를 찾아 이미지를 보여준다.
    for i in range(len(winpick_champ)):
        if not winpick_champ[i] in statistics:
            statistics.append((winpick_champ[i], floor(float(winratio[i].strip('%')) * float(pickratio[i].strip('%'))) / 100))
    statistics = sorted(statistics, key=itemgetter(1), reverse=True)
    keywords = ["OP 챔피언 추천 Top 10"]
    for i in range(1, 11):
        keywords.append(str(i) + "위: " + statistics[i - 1][0] + "\t\t추천지수: " + str(statistics[i - 1][1]))
    slack.files.upload(statistics[0][0].replace(" ", "") + '.png', channels="day4")

    return u'\n'.join(keywords)

'''
챔피언을 추천해달라는 명령어 이외의 명령어에 대한 작업을 수행하는 함수로
승률, 픽률, 밴률을 기반으로 각 승, 픽, 밴 인텐트가 호출 되고 인텐트의 종류에 따라
반환하는 상위 10개 챔피언의 정렬 기준도 승률, 픽률, 밴률에 따라 달라진다.
'''
def crawl_opgg_top10(intent):
    # 추천 지수 함수와 같은 방식으로 작성
    if intent == 'Default Fallback Intent':
        return ''

    keywords = []
    statistics = []
    statistics_ban = []

    sourcecode1 = urllib.request.urlopen(
        'http://www.op.gg/champion/ajax/statistics/trendChampionList/type=winratio&').read()
    soup1 = BeautifulSoup(sourcecode1, "html.parser")

    # 밴률 페이지가 따로 존재하므로 밴 페이지를 따로 받아준다.
    sourcecode2 = urllib.request.urlopen(
        'http://www.op.gg/champion/ajax/statistics/trendChampionList/type=banratio&').read()
    soup2 = BeautifulSoup(sourcecode2, "html.parser")

    winpick_champ = [i.get_text() for i in soup1.find_all("div", class_="champion-index-table__name")]
    winpick_champ = winpick_champ[:142]
    winratio = [i.get_text() for i in soup1.find_all("td",
                                                     class_="champion-index-table__cell champion-index-table__cell--value champion-index-table__cell--blue")]
    winratio = winratio[:142]
    pickratio = [i.get_text() for i in
                 soup1.find_all("td", class_="champion-index-table__cell champion-index-table__cell--value")]
    pickratio = pickratio[:142]

    ban_champ = [i.get_text() for i in soup2.find_all("div", class_="champion-index-table__name")]
    ban_champ = ban_champ[:142]
    banratio = [i.get_text() for i in soup2.find_all("td",
                                                     class_="champion-index-table__cell champion-index-table__cell--value champion-index-table__cell--blue")]
    banratio = banratio[:142]

    for i in range(len(winpick_champ)):
        if not winpick_champ[i] in statistics:
            statistics.append((winpick_champ[i], float(winratio[i].strip('%')), float(pickratio[i].strip('%'))))

    for i in range(len(ban_champ)):
        if not ban_champ[i] in statistics:
            statistics_ban.append((ban_champ[i], float(banratio[i].strip('%'))))

    # 인텐트의 내용에 따라 승, 픽, 밴인지 나누어서 출력되는 결과를 다르게 한다.
    if intent == '승':
        statistics = sorted(statistics, key=itemgetter(1), reverse=True)
        keywords = ["챔피언 승률 Top 10"]
        slack.files.upload(statistics[0][0].replace(" ", "") + '.png', channels="day4")
        for i in range(1, 11):
            keywords.append(str(i) + "위: " + statistics[i-1][0] + "\t\t승률: " + str(statistics[i-1][1]) + "%")
    if intent == '픽':
        statistics = sorted(statistics, key=itemgetter(2), reverse=True)
        keywords = ["챔피언 픽률 Top 10"]
        slack.files.upload(statistics[0][0].replace(" ", "") + '.png', channels="day3")
        for i in range(1, 11):
            keywords.append(str(i) + "위: " + statistics[i-1][0] + "\t\t픽률: " + str(statistics[i-1][2]) + "%")
    if intent == '밴':
        statistics_ban = sorted(statistics_ban, key=itemgetter(1), reverse=True)
        print(statistics_ban)
        keywords = ["챔피언 밴률 Top 10"]
        slack.files.upload(statistics_ban[0][0].replace(" ", "") + '.png', channels="day4")
        for i in range(1, 10):
            keywords.append(str(i) + "위: " + statistics_ban[i-1][0] + "\t\t밴률: " + str(statistics_ban[i-1][1]) + "%")

    # 한글 지원을 위해 앞에 unicode u를 붙혀준다.
    return u'\n'.join(keywords)

def get_answer(text, user_key):
    data_send = {
        'query': text,
        'sessionId': user_key,
        'lang': 'ko',
    }

    data_header = {
        'Authorization': 'Bearer 37dc131c28f940459853c4ecd1b190bc',
        'Content-Type': 'application/json; charset=utf-8'
    }

    dialogflow_url = 'https://api.dialogflow.com/v1/query?v=20150910'
    res = requests.post(dialogflow_url, data=json.dumps(data_send), headers=data_header)

    if res.status_code != requests.codes.ok:
        return '오류가 발생했습니다.'

    data_receive = res.json()
    result = {
        "speech": data_receive['result']['fulfillment']['speech'],
        "intent": data_receive['result']['metadata']['intentName']
    }
    print(result)
    return result

# 이벤트 핸들하는 함수
def _event_handler(event_type, slack_event):
    print(slack_event["event"])

    if event_type == "app_mention":
        channel = slack_event["event"]["channel"]
        text = slack_event["event"]["text"]
        text = text[13:]
        answer = get_answer(text, 'session')

        # 명령어가 요구하는 사항에 따라 인텐트를 다르게 하여 추천 지수 함수로 갈 것인지
        # 승, 픽, 밴률 탑텐 함수로 갈 것인지 결정한다.
        if answer['intent'] == '추천':
            keywords = crawl_opgg_recommend(answer['intent'])
        else:
            keywords = crawl_opgg_top10(answer['intent'])
        sc.api_call(
            "chat.postMessage",
            channel=channel,
            text= answer['speech'] + "\n" + keywords
        )

        return make_response("App mention message has been sent", 200, )

    # ============= Event Type Not Found! ============= #
    # If the event_type does not have a handler
    message = "You have not added an event handler for the %s" % event_type
    # Return a helpful error message
    return make_response(message, 200, {"X-Slack-No-Retry": 1})


@app.route("/listening", methods=["GET", "POST"])
def hears():
    slack_event = json.loads(request.data)

    if "challenge" in slack_event:
        return make_response(slack_event["challenge"], 200, {"content_type":
                                                                 "application/json"
                                                             })

    if slack_verification != slack_event.get("token"):
        message = "Invalid Slack verification token: %s" % (slack_event["token"])
        make_response(message, 403, {"X-Slack-No-Retry": 1})

    if "event" in slack_event:
        event_type = slack_event["event"]["type"]
        return _event_handler(event_type, slack_event)

    # If our bot hears things that are not events we've subscribed to,
    # send a quirky but helpful error response
    return make_response("[NO EVENT IN SLACK REQUEST] These are not the droids\
                         you're looking for.", 404, {"X-Slack-No-Retry": 1})


@app.route("/", methods=["GET"])
def index():
    return "<h1>Server is ready.</h1>"

if __name__ == '__main__':
    app.run('0.0.0.0', port=8080)