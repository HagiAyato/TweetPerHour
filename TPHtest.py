#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import config
import os
import sys
import datetime as dt
import pandas as pd
from requests_oauthlib import OAuth1Session

# OAuth認証部分
CK = config.CONSUMER_KEY
CS = config.CONSUMER_SECRET
AT = config.ACCESS_TOKEN
ATS = config.ACCESS_TOKEN_SECRET
twitter = OAuth1Session(CK, CS, AT, ATS)

# タイムゾーン定義(JST)
tz_JST = dt.timezone(dt.timedelta(hours=+9), 'JST')

# Twitter Endpoint(検索結果を取得する)
url_get = 'https://api.twitter.com/1.1/search/tweets.json'
url_post = 'https://api.twitter.com/1.1/statuses/update.json'

# Enedpointへ渡すパラメーター
print('検索ワードを入力：')
name = input()
keyword = name + ' OR #' + name + ' -filter:retweets'
# since - until 出期間指定。過去一週間のみ？
# https://ja.stackoverflow.com/questions/33254/twitter-api%E3%81%A7%E5%8F%96%E5%BE%97%E3%81%A7%E3%81%8D%E3%82%8B%E3%83%84%E3%82%A4%E3%83%BC%E3%83%88%E3%81%AF%E4%BD%95%E6%97%A5%E5%89%8D%E3%81%BE%E3%81%A7%E3%81%A7%E3%81%99%E3%81%8B
params = {
    'count' : 100,      # 取得するtweet数(上限100)
    'q'     : keyword  # 検索キーワード
    }

# 検索ワードを表示
print('単語名：' + keyword)
# 検索実行
req = twitter.get(url_get, params = params)

# 検索成功か判定
if req.status_code == 200:
    #現在時刻
    ptdatetime = dt.datetime.now(tz_JST)
    #遡り最後のツイート時刻(初期値は現在時刻)
    tdatetime = ptdatetime
    # ② 取得した検索結果ツイート件数
    num = 0
    #検索結果ツイート全件ループ
    res = json.loads(req.text)
    for i,line in enumerate(res['statuses']):
        # ツイートの時刻を取得 文字列->日付時刻変換+timezone設定
        tdatetime = dt.datetime.strptime(line['created_at'],'%a %b %d %H:%M:%S %z %Y').astimezone(tz_JST)
        # ツイート件数カウンタ++
        num = num + 1
        print(str(i) + '件目******' + str(tdatetime))
        print(line['text'] + '\n')
    # ① 現在時刻～一番遡ったツイートの時刻の時間差(h)
    ttime = (ptdatetime - tdatetime).total_seconds() / 3600
    print('遡り時間(h)：' + str(ttime) + '件数(件)：' + str(num))

    # 集計(集計結果0件の場合は0除算防止のため計算しない)
    if 0 < num :
        # ツイート時速 = ② 取得ツイート数 / ① 時間差
        tweetperhour = num / ttime
        # ツイート時速を出力
        print('時速(tweet/h)：' + str(tweetperhour))
    else:
        print("Failed: %d" % req.status_code)
# キー入力を待って終了
input()