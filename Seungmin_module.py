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

slack_token = "xoxb-503818135714-507351131987-GyVOyX3uF6Pzv1N4yT5X9dKn"
slack_client_id = "503818135714.507348823507"
slack_client_secret = "8194f60277b7af2f46584293915e356b"
slack_verification = "hgtt6xtPYcb4Oq5TzDPhYFOr"
sc = SlackClient(slack_token)
slack = Slacker(slack_token)

def crawl_opgg_recommend(intent):
    if intent == 'Default Fallback Intent':
        return ''

    keywords = []
    statistics = []

    sourcecode1 = urllib.request.urlopen(
        'http://www.op.gg/champion/ajax/statistics/trendChampionList/type=winratio&').read()
    soup1 = BeautifulSoup(sourcecode1, "html.parser")
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

    for i in range(len(winpick_champ)):
        if not winpick_champ[i] in statistics:
            statistics.append((winpick_champ[i], floor(float(winratio[i].strip('%')) * float(pickratio[i].strip('%'))) / 100))
    statistics = sorted(statistics, key=itemgetter(1), reverse=True)
    keywords = ["OP 챔피언 추천 Top 10"]
    for i in range(1, 11):
        keywords.append(str(i) + "위: " + statistics[i - 1][0] + "\t\t추천지수: " + str(statistics[i - 1][1]))
    slack.files.upload(statistics[0][0].replace(" ", "") + '.png', channels="day4")

    return u'\n'.join(keywords)
def crawl_opgg_top10(intent):
    if intent == 'Default Fallback Intent':
        return ''

    keywords = []
    statistics = []
    statistics_ban = []

    sourcecode1 = urllib.request.urlopen(
        'http://www.op.gg/champion/ajax/statistics/trendChampionList/type=winratio&').read()
    soup1 = BeautifulSoup(sourcecode1, "html.parser")
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

    if intent == '승':
        statistics = sorted(statistics, key=itemgetter(1), reverse=True)
        keywords = ["챔피언 승률 Top 10"]
        slack.files.upload(statistics[0][0].replace(" ", "") + '.png', channels="day4")
        for i in range(1, 11):
            keywords.append(str(i) + "위: " + statistics[i-1][0] + "\t\t승률: " + str(statistics[i-1][1]) + "%")
    if intent == '픽':
        statistics = sorted(statistics, key=itemgetter(2), reverse=True)
        keywords = ["챔피언 픽률 Top 10"]
        slack.files.upload(statistics[0][0].replace(" ", "") + '.png', channels="day4")
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