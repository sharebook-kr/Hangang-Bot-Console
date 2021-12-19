import pyupbit
import time
import datetime

DELAY = 0.2           
TS_MARGIN = 0.80      # 고점 대비 20% 하락시 매도 

with open("account_upbit.txt") as f:
    lines = f.readlines()
    access = lines[0].strip()
    secret = lines[1].strip()

# 원화 잔고 조회
upbit = pyupbit.Upbit(access, secret)
krw_balance = upbit.get_balance(ticker="KRW")

prev_tickers = pyupbit.get_tickers()
time.sleep(DELAY)


def buy_market_order(ticker, krw_balance):
    # 오더북 조회
    orderbook = pyupbit.get_orderbook(ticker)
    orderbook_units = orderbook['orderbook_units']
    order0 = orderbook_units[0]
    ask0_price = order0['ask_price']      # 매도 1호가 가격

    # 지정가 매수 
    volume = int(krw_balance / ask0_price)
    upbit.buy_limit_order(ticker, ask0_price, volume)


def sell_market_order(ticker, volume):
    # 오더북 조회
    orderbook = pyupbit.get_orderbook(ticker)
    orderbook_units = orderbook['orderbook_units']
    order0 = orderbook_units[0]
    bid0_price = order0['bid_price']      # 매도 1호가 가격

    # 지정가 매도 
    upbit.sell_limit_order(ticker, bid0_price, volume)


while True:
    now = datetime.datetime.now()
    try:
        curr_tickers = pyupbit.get_tickers()
        diff_set = set(curr_tickers) - set(prev_tickers)
    except:
        time.sleep(10)
        continue

    if len(diff_set) == 0:
        print(now, "| 업비트 신규 상장 감시 중 | ", "잔고: ", int(krw_balance))
        time.sleep(DELAY)
        continue
    else:
        ticker = diff_set.pop()
        print("신규 상장: ", ticker)

        # 신규상장 암호화폐 시장가 매수
        print("신규 상장 5분 대기 중")
        time.sleep(60 * 5)          # 신규 상장 후 5분 거래 안됨 

        # 오더북 조회 후 매도 1호가 가격으로 지정가 주문
        buy_market_order(ticker, krw_balance)
        time.sleep(DELAY)

        coin_balance = upbit.get_balance(ticker)
        high_price = pyupbit.get_current_price(ticker)
        time.sleep(DELAY)

        while True:
            curr_price = pyupbit.get_current_price(ticker)

            # Trailing stop
            if (curr_price < (high_price * TS_MARGIN)):
                # 고점대비 설정값 만큼 하락시 매도 
                # 오더북 조회 후 매수 1호가 가격으로 지정가 주문
                sell_market_order(ticker, coin_balance)
                break

            high_price = max(high_price, curr_price)
            time.sleep(DELAY)
        
        # 바깥 while loop로 이동  
        krw_balance = upbit.get_balance(ticker="KRW")    # 신규 상장 코인 감시하기 전에 잔고 업데이트 필요
        continue


