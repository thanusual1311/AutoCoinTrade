import pyupbit
import datetime
import time
import telegram
import pandas as pd
import numpy as np
from telegram.ext import Updater
from telegram.ext import MessageHandler, Filters


class MyError(Exception):
    pass


def sell_all_coin():
    global sellOk
    if sellOk == False:
        my_balance_list = get_my_balance_list()
        if my_balance_list is not None:  # 보유코인이 있다면
            for i in range(0, len(my_balance_list)):  # 루프 돌면서 보유코인 매도
                try:
                    desc = sell_crypto_currency(upbit, "KRW-" + my_balance_list[i])  # 매도요청
                    if len(desc) == 1:
                        ackTelegramMSG("VW 전량매도 에러, MESSAGE : " + desc['error']['message'])
                        raise MyError()
                    elif len(desc) != 15:
                        ackTelegramMSG("VW 전량매도 알 수 없는 에러")
                        raise MyError()
                    # 정상메세지 발송
                    # result = upbit.get_order(desc['uuid'])
                    # ackTelegramMSG("매도( "+ desc['uuid'] + " ), 마켓 : " + result['market'] + ", 상태 : " + result['state'] + ", 금액 : " + result['trades'][0]['funds'])
                    time.sleep(0.7)
                except:
                    pass
        sellOk = True


def get_my_balance_list():
    balance_list = upbit.get_balances()
    currency_list = []
    for i in range(0, len(balance_list)):
        if balance_list[i]['unit_currency'] == 'KRW':
            if balance_list[i]['currency'] != 'KRW':
                time.sleep(0.2)
                tempdf = pyupbit.get_ohlcv("KRW-" + balance_list[i]['currency'], count=1)
                if tempdf is not None:
                    currency_list.append(balance_list[i]['currency'])
    return currency_list


def handler(update, context):
    user_text = update.message.text  # 사용자가 보낸 메세지를 user_text 변수에 저장합니다.
    user_text_header = user_text[0:1].upper()
    if user_text_header == "H":
        # conmmand list
        # bot.send_message(chat_id=telgm_chat_id, text="h : help\nt : target coin list")  # 답장 보내기
        ackTelegramMSG("h : help\n" +
                       "t : setting info\n" +
                       "i : insert target coin\n" +
                       "    ex) i BTC 1 (BTC를 1순위로 INSERT)\n" +
                       "    ex) i BTC (BTC를 APPEND)\n" +
                       "d : delete target coin\n" +
                       "    ex) d 1 (1번 타겟코인 DELETE)\n" +
                       "c : max buy coin\n" +
                       "    ex) c 1 (최대 투자 코인 수)\n" +
                       "w : 투자 기동 여부\n" +
                       "    ex) w 0 (투자 기동 종료)\n" +
                       "    ex) w 1 (투자 기동 실행)\n" +
                       "e : 긴급 전량 매도\n"
                       "r : 수익률 랭킹 조회\n" +
                       "    ex) r 300 10 (60분 캔들 300개 기준\n" +
                       "                  랭킹 10위 조회)")

    elif user_text_header == "T":
        # target coin list
        global max_buy_target_cnt
        global DO_WORK
        ackTelegramMSG(list_to_strings("내 타겟 코인", my_target_coin_list))
        ackTelegramMSG("최대 투자 코인 타입수  : " + str(max_buy_target_cnt))
        ackTelegramMSG("투자 기동 여부  : " + str(DO_WORK))
    elif user_text_header == "I":
        # 타겟코인 추가
        try:
            s = user_text.split()
            if len(s) == 2:
                kk = pyupbit.get_ohlcv("KRW-" + s[1].upper(), count=1)
                if kk is None:
                    raise MyError()
                isExists = False
                for i in my_target_coin_list:
                    if i == s[1].upper():
                        ackTelegramMSG("이미 타겟에 존재하는 코인입니다.( " + s[1].upper() + " )")
                        isExists = True
                if isExists == False:
                    my_target_coin_list.append(s[1].upper())
                    ackTelegramMSG(list_to_strings("내 타겟 코인", my_target_coin_list))
            elif len(s) == 3:
                kk = pyupbit.get_ohlcv("KRW-" + s[1].upper(), count=1)
                if kk is None:
                    raise MyError()
                isExists = False
                for i in my_target_coin_list:
                    if i == s[1].upper():
                        ackTelegramMSG("이미 타겟에 존재하는 코인입니다.( " + s[1].upper() + " )")
                        isExists = True
                if isExists == False:
                    my_target_coin_list.insert(int(s[2]) - 1, s[1].upper())
                    ackTelegramMSG(list_to_strings("내 타겟 코인", my_target_coin_list))
            else:
                ackTelegramMSG("명령을 이해하지 못했습니다.")
        except:
            ackTelegramMSG("명령을 이해하지 못했습니다.")
            pass
    elif user_text_header == "D":
        # 타겟코인 삭제
        try:
            s = user_text.split()
            del my_target_coin_list[int(s[1]) - 1]
            ackTelegramMSG(list_to_strings("내 타겟 코인", my_target_coin_list))
        except:
            ackTelegramMSG("명령을 이해하지 못했습니다.")
            pass
    elif user_text_header == "C":
        # 최대 투자 코인 타입수
        try:
            s = user_text.split()
            max_buy_target_cnt = int(s[1])
            ackTelegramMSG("최대 투자 코인 타입수  : " + str(max_buy_target_cnt))
        except:
            ackTelegramMSG("명령을 이해하지 못했습니다.")
            pass
    elif user_text_header == "W":
        # 최대 투자 코인 타입수
        try:
            s = user_text.split()
            if int(s[1]) == 0:
                DO_WORK = False
            else:
                DO_WORK = True
            ackTelegramMSG("투자 기동 여부  : " + str(DO_WORK))
        except:
            ackTelegramMSG("명령을 이해하지 못했습니다.")
            pass
    elif user_text_header == "E":
        sell_all_coin()
        ackTelegramMSG("전량매도 호출완료")
    elif user_text_header == "R":
        # 최대 투자 코인 타입수
        try:
            s = user_text.split()
            if len(s) == 3:
                ackTelegramMSG(get_ma3_rank(int(s[1]), int(s[2])))
            else:
                ackTelegramMSG("명령을 이해하지 못했습니다.")
        except:
            ackTelegramMSG("명령을 이해하지 못했습니다.")
            pass
    else:
        # else
        ackTelegramMSG("명령을 이해하지 못했습니다.")


def list_to_strings(title, target_list):
    """
    메세지 발송용 문자열 반환
    """
    returnmsg = "< " + title + " >\n"
    for i in range(0, len(target_list)):
        returnmsg = returnmsg + str(i + 1) + " : " + target_list[i] + "\n"
    return returnmsg


def buy_crypto_currency(upbit, ticker, krw):
    # krw = upbit.get_balance()
    # krw = int(int(krw)/10000)*10000
    return upbit.buy_market_order(ticker, krw)


def sell_crypto_currency(upbit, ticker):
    """
    전량매도 함수
    """
    unit = upbit.get_balance(ticker)
    return upbit.sell_market_order(ticker, unit)


def get_ma3(tick):
    """
    한시간 봉을 받아 그룹핑 해서 일봉으로 만든다
    일봉은 09시 기준이지만 00시에 동작하도록 하기 위함.
    """

    dfup = pyupbit.get_ohlcv("KRW-" + tick, "minute60")
    dfup['N_INDEX'] = dfup.index
    dfup['N_INDEX2'] = pd.to_datetime(dfup['N_INDEX'].dt.date)

    df_MAX = dfup['high'].groupby(dfup["N_INDEX2"]).max()
    df_MIN = dfup['low'].groupby(dfup["N_INDEX2"]).min()
    df_cnt = dfup['open'].groupby(dfup["N_INDEX2"]).count()
    dframe = pd.DataFrame(df_MAX)
    dframe['low'] = pd.DataFrame(df_MIN)
    dframe['cnt'] = pd.DataFrame(df_cnt)
    dframe.insert(3, 'open', 0, True)
    dframe.insert(4, 'close', 0, True)
    dframe['N_INDEX'] = dframe.index

    for i in dframe['N_INDEX']:
        j = dfup[dfup['N_INDEX2'] == i]
        open_val = j['open'][0]
        close_val = j['close'][-1]
        index_val = j['N_INDEX2'][0]
        dframe['open'] = np.where(dframe['N_INDEX'] == index_val,
                                  open_val,
                                  dframe['open'])
        dframe['close'] = np.where(dframe['N_INDEX'] == index_val,
                                   close_val,
                                   dframe['close'])

    """
    3일 기준 이동평균 계산 
    """
    dframe['ma3_close'] = dframe['close'].rolling(window=3).mean().shift(1)
    # return dframe.iloc[-1]['ma3_close']
    return dframe


def ackTelegramMSG(strMSG):
    # strMSG = strMSG + " <" + datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + ">"
    bot.sendMessage(chat_id=telgm_chat_id, text=strMSG)

def get_ma3_rank(cnt = 300, rank_cnt = 10):
   """
   한시간 봉을 받아 그룹핑 해서 일봉으로 만든다
   일봉은 09시 기준이지만 00시에 동작하도록 하기 위함.
   """
   hprs = []

   tickList = pyupbit.get_tickers("KRW")
   for tick in tickList:
       # dfup = pyupbit.get_ohlcv("KRW-"+tick,"minute60")
       dfup = pyupbit.get_ohlcv(tick, "minute60", cnt)
       dfup['N_INDEX'] = dfup.index
       dfup['N_INDEX2'] = pd.to_datetime(dfup['N_INDEX'].dt.date)

       df_MAX = dfup['high'].groupby(dfup["N_INDEX2"]).max()
       df_MIN = dfup['low'].groupby(dfup["N_INDEX2"]).min()
       df_cnt = dfup['open'].groupby(dfup["N_INDEX2"]).count()
       dframe = pd.DataFrame(df_MAX)
       dframe['low'] = pd.DataFrame(df_MIN)
       dframe['cnt'] = pd.DataFrame(df_cnt)
       dframe.insert(3, 'open', 0, True)
       dframe.insert(4, 'close', 0, True)
       dframe['N_INDEX'] = dframe.index

       for i in dframe['N_INDEX']:
           j = dfup[dfup['N_INDEX2'] == i]
           open_val = j['open'][0]
           close_val = j['close'][-1]
           index_val = j['N_INDEX2'][0]
           dframe['open'] = np.where(dframe['N_INDEX'] == index_val,
                                     open_val,
                                     dframe['open'])
           dframe['close'] = np.where(dframe['N_INDEX'] == index_val,
                                      close_val,
                                      dframe['close'])

       """
       3일 기준 이동평균 계산 
       """
       dframe['ma3_close'] = dframe['close'].rolling(window=3).mean().shift(1)
       dframe['bull'] = dframe['open'] > dframe['ma3_close']
       fee = 0.0032
       dframe['ror'] = np.where(dframe['bull'],
                                dframe['close'] / dframe['open'] - fee,
                                1)

       dframe['hpr'] = dframe['ror'].cumprod()

       hprs.append((tick, dframe['hpr'][-2], dframe['bull'][-1]))

   sorted_hprs = sorted(hprs, key=lambda x:x[1], reverse=True)
   sorted_hprs = sorted_hprs[:rank_cnt]
   result_str = ""
   for i in range(0, len(sorted_hprs)):
       result_str = result_str + sorted_hprs[i][0] +", " + str(sorted_hprs[i][1]) + ", " + str(sorted_hprs[i][2]) + "\n"

   return result_str

tick = "XRP"

with open("AutoCoinTrade.txt") as f:
    lines = f.readlines()
    apikey = lines[0].strip()
    seckey = lines[1].strip()
    telgm_token = lines[2].strip()
    telgm_chat_id = lines[3].strip()

upbit = pyupbit.Upbit(apikey, seckey)
bot = telegram.Bot(token=telgm_token)

sellOk = False
buyOk = False
max_buy_target_cnt = 5
my_target_coin_list = ['ETH', 'XRP', 'ETC', 'BTC', 'LTC', 'LINK']

# ackTelegramMSG(list_to_strings("내 타겟 코인", my_target_coin_list))

updater = Updater(token=telgm_token, use_context=True)
dispatcher = updater.dispatcher
updater.start_polling()
echo_handler = MessageHandler(Filters.text, handler)
dispatcher.add_handler(echo_handler)

ackTelegramMSG("********  PROGRAM START  ********")
ackTelegramMSG(list_to_strings("내 타겟 코인", my_target_coin_list))
ackTelegramMSG("최대 투자 코인 타입수  : " + str(max_buy_target_cnt))
ackTelegramMSG("********  HELP : 'h' or 'H'  ********")

my_balance_list = get_my_balance_list()
tick_banlance = upbit.get_balance("KRW")

DO_WORK = True

while True:
    now = datetime.datetime.now()
    mid = datetime.datetime(now.year, now.month, now.day)
    mid = mid + datetime.timedelta(seconds=1)
    if mid < now < mid + datetime.timedelta(seconds=10) and DO_WORK:
        sell_all_coin()

        # if sellOk == False:
        #     my_balance_list = get_my_balance_list()
        #     if my_balance_list is not None: # 보유코인이 있다면
        #         for i in range(0, len(my_balance_list)): # 루프 돌면서 보유코인 매도
        #             try:
        #                 desc = sell_crypto_currency(upbit, "KRW-"+my_balance_list[i])  # 매도요청
        #                 if len(desc) == 1:
        #                     ackTelegramMSG("VW 전량매도 에러, MESSAGE : " + desc['error']['message'])
        #                     raise MyError()
        #                 elif len(desc) != 15:
        #                     ackTelegramMSG("VW 전량매도 알 수 없는 에러")
        #                     raise MyError()
        #                 # 정상메세지 발송
        #                 # result = upbit.get_order(desc['uuid'])
        #                 # ackTelegramMSG("매도( "+ desc['uuid'] + " ), 마켓 : " + result['market'] + ", 상태 : " + result['state'] + ", 금액 : " + result['trades'][0]['funds'])
        #                 time.sleep(0.7)
        #             except:
        #                 pass
        #     sellOk = True
    elif mid + datetime.timedelta(seconds=10) < now < mid + datetime.timedelta(seconds=20) and DO_WORK:
        if buyOk == False:
            tick_banlance = upbit.get_balance("KRW")  # 한화 보유액
            # krw_per_each = int(int(int(tick_banlance) / 10000) / max_buy_target_cnt) * 10000   # 한화 보유액을 최대 투자 코인수로 나눔. 만원미만 절사
            krw_per_each = int(tick_banlance / max_buy_target_cnt)  # 한화 보유액을 최대 투자 코인수로 나눔. 소수점 버림
            buyOk_cnt = 0

            for k in range(0, len(my_target_coin_list)):
                time.sleep(0.5)
                if buyOk_cnt < max_buy_target_cnt:  # 최대 투자 코인수 만큼 샀는가
                    tick = my_target_coin_list[k]  # 매수 대상 코인

                    priceFrame = get_ma3(tick)
                    targetPrice = priceFrame.iloc[-1]['ma3_close']
                    openPrice = priceFrame.iloc[-1]['open']
                    try:
                        if targetPrice < openPrice:
                            desc = buy_crypto_currency(upbit, "KRW-" + tick, krw_per_each)
                            if len(desc) == 1:
                                ackTelegramMSG("전량매수 에러, MESSAGE : " + desc['error']['message'])
                                raise MyError()
                            elif len(desc) != 15:
                                ackTelegramMSG("전량매수 알 수 없는 에러")
                                raise MyError()
                            # 정상메세지 발송
                            # result = upbit.get_order(desc['uuid'])
                            # ackTelegramMSG("매수( "+ desc['uuid'] + " ), 마켓 : " + result['market'] + ", 상태 : " + result['state'] + ", 금액 : " + result['trades'][0]['funds'])
                            buyOk_cnt = buyOk_cnt + 1
                    except:
                        pass
            # 안사질까바 한번 더 돌림. 로직 좀 멋지게 바꿔보자..
            for k in range(0, len(my_target_coin_list)):
                time.sleep(0.5)
                if buyOk_cnt < max_buy_target_cnt:  # 최대 투자 코인수 만큼 샀는가
                    tick = my_target_coin_list[k]  # 매수 대상 코인

                    priceFrame = get_ma3(tick)
                    targetPrice = priceFrame.iloc[-1]['ma3_close']
                    openPrice = priceFrame.iloc[-1]['open']
                    try:
                        if targetPrice < openPrice:
                            desc = buy_crypto_currency(upbit, "KRW-" + tick, krw_per_each)
                            if len(desc) == 1:
                                ackTelegramMSG("전량매수 에러, MESSAGE : " + desc['error']['message'])
                                raise MyError()
                            elif len(desc) != 15:
                                ackTelegramMSG("전량매수 알 수 없는 에러")
                                raise MyError()
                            # 정상메세지 발송
                            # result = upbit.get_order(desc['uuid'])
                            # ackTelegramMSG("매수( "+ desc['uuid'] + " ), 마켓 : " + result['market'] + ", 상태 : " + result['state'] + ", 금액 : " + result['trades'][0]['funds'])
                            buyOk_cnt = buyOk_cnt + 1
                    except:
                        pass
            buyOk = True
    else:
        buyOk = False
        sellOk = False

    time.sleep(1)