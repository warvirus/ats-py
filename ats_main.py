# This file is protected under the GNU General Public License version 2.0 (GPL-2.0).
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/gpl-2.0.html>.
#
# Author : Jaosn Lee  2023.08
# Copyright(c) 2023-2025 Aistock, Co. All rights reserved.
#
# This software and its source code are released under the terms of the GPL-2.0 license.
# For more details about GPL-2.0, please visit https://www.gnu.org/licenses/gpl-2.0.html.
#
# This program is distributed WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#

# /usr//bin/python
# -*- coding: utf-8 -*-

from ats_ui import *
import sys

# from utils import get_macd
import utils as util
from ats_conn import tcp_client, PORT
from ats_conn import MSG, END, HOGA, TXT, PROTO_CMD, PROTO_MSG, PROTO_TXT

# 출처 : https://4uwingnet.tistory.com/13
def my_exception_hook(exctype, value, traceback):
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    # sys.exit(1)

def parse_stoploss(step_stoploss_str):
    step_stoploss = []
    try:
        tmp = []
        for x in step_stoploss_str.split('|'):
            xx =  [float(x.strip()) for x in x.split(',')] if len(x) >=1 else []
            if len(xx) >= 2:
                tmp.append(xx[:2])
        step_stoploss = tmp.copy()
    except Exception as x:
        print('parse_stoploss(x) : {} - "{}"'.format(x.__class__.__name__, step_stoploss_str))
        logging.error('parse_stoploss(x) : {} - "{}"'.format(x.__class__.__name__, step_stoploss_str))

    return step_stoploss

class ATSWnd(WindowClass):
    def __init__(self, opt: opt_struct):
        # 초기화...
        super().__init__(opt)

        self._trade_func_method['methods'] = {
                '1': {'name': '단타매매', 'start': '0900', 'end': '1130', "func": None,
                      'option': {'매도조건': '고정대비'}},
                '2': {'name': '스윙매매', 'start': '0900', 'end': '1310', "func": None,
                      'option': {'매도조건': '평균단가'}},
                '3': {'name': '지능형매매', 'start': '0900', 'end': '1310', "func": None,
                      'option': {'매도조건': '지능형'}},
                '4': {'name': 'MACD매매', 'start': '1300', 'end': '1310', "func": self._trade_macd,
                      'option': {'매도조건': '매수후'}}
            }
        self._trade_func_method['default'] = '4'

        # 외부 컴퓨터와 통신을 하기 위한 코드
        self.client = None
        if (self.opt.use_external_srv):
            self.client = tcp_client()

            port = PORT
            server_ip = 'localhost'
            
            # 외부 주소 사용 ?
            if self.opt.external_server != '':
                n = self.opt.external_server.find(':')
                if (n > 0):
                    port = self.opt.external_server[n+1:]
                    server_ip = self.opt.external_server[:n]

            self.client.connect(server_ip, port, user_callback=self.recv_msg)
             
    def do_periodic_check(self, config, now_s, is_available_trading):
        """
        10 분마다.(미체결 취소)
        """
        if is_available_trading:
            jan_list = self.get_che_jan_list(self.ats.account_num)
            cnt = len(jan_list)
            for i in range(cnt):
                hour = int(now_s[0:2]) - int(jan_list['시간'][i][0:2])
                if hour > 0:
                    hour -= 1
                    minute = int(now_s[2:4]) + (60-int(jan_list['시간'][i][2:4]))  
                else:
                    minute = int(now_s[2:4]) - int(jan_list['시간'][i][2:4])
                diff =  (hour * 60) + minute
                print('{}- 주문번호 {}, 종목코드: {}, 주문수량: {}, 주문구분: {},  미체결수량 : {}, 원주문번호: {}, 시간: {}, 경과시간 {} '.format(jan_list['계좌번호'][i]
                                                                , jan_list['주문번호'][i], jan_list['종목코드'][i], jan_list['주문수량'][i]
                                                                , jan_list['주문구분'][i], jan_list['미체결수량'][i], jan_list['원주문번호'][i]
                                                                , jan_list['시간'][i]
                                                                , diff))

                # 10분 지난 매수는 취소 한다.  
                cancel_time = config['매매취소'] if '매매취소' in config else 10           
                if diff > 10 and (jan_list['주문구분'][i] == '+매수'):
                    self.ats.set_order(jan_list['계좌번호'][i], jan_list['종목코드'][i], 
                                    "매수취소", abs(int(jan_list['미체결수량'][i])), abs(int(jan_list['주문가격'][i])),
                                        "시장가", org_orderNo=jan_list['주문번호'][i]) 
                    sleep_ms(500)  #  과부하방지
              
    def do_trade_processing(self, config, now_s, is_available_trading):
        """
        자동 트레이딩을 한다.
        """

        # 자동매매 실행
        logging.debug('자동트레이딩 ........ {}'.format(now_s))


        # -------------------- 모든 데이터 상태값을 검증 한다. -------------------- #
        buy_stocks = []

        max_amount = config['buy']['max-amount']
        for code, trade_stock in self.trade_stocks.stocks.items():

            # if self.client is not None:
            #    if self.client.send(MSG, msg=json.dumps(trade_stock, ensure_ascii=False)) == False:
            #        self.client.reconnect()
     
            # 자동매매 중지 ?
            if self.auto_analysis == False:
                break

            # if NEW_STOCK in trade_stock and trade_stock[NEW_STOCK] is True:
    
            # # 일봉 MACD 종목 트레이팅
            # if OHLC_DAILY in trade_stock and trade_stock[OHLC_DAILY] is not None \
            #         and len(trade_stock[OHLC_DAILY]) > 30:
            #self._trade_process(code, trade_stock, config, max_amount, now_s)

            # # 분봉 MACD(단타용) 트레이딩
            # elif OHLC_MINUTE1 in trade_stock and trade_stock[OHLC_MINUTE1] is not None \
            #         and len(trade_stock[OHLC_MINUTE1]) > 30:
            #     self._trade_process(code, trade_stock, trade_stock[OHLC_MINUTE1], config, max_amount, now_s)

            b_buy_trading, cnt, price, desc = self._trade_process(code, trade_stock, config, max_amount, now_s, is_available_trading)
            if b_buy_trading:
                buy_stocks.append([code, cnt, price, desc])

            # 계산 결과값 화면에 출력
            # self.disp_realtime_sise(code)

        # _trade_process
        cnt_limit = config['buy']['max-stocks']
        for lst in buy_stocks:
            code = lst[0]
            buy_cnt = lst[1]
            price = lst[2]
            desc = lst[3]

            ## ban ?
            if 'ban' in config['buy'] and code in config['buy']['ban']:
                logging.info('ban : {}'. format(desc))
                continue

             # code, b_buy_trading, cnt, price, desc, 현재가가 있는 것만 구한다.
            if code in self.trade_stocks.stocks and buy_cnt > 0 \
                and ('현재가' in self.trade_stocks.stocks[code] and self.trade_stocks.stocks[code]['현재가'] > 0):
                
                name = self.trade_stocks.stocks[code][DESC_STOCK]['name']
                buy_price = self.trade_stocks.stocks[code]['현재가']
                buy_cnt = int(price / buy_price)         # 구매수량을 재설정한다.
                
                # buy_cnt = int(max_amount / price)
                if buy_cnt > 0 and buy_price > 0:
                    if self.ats.trade_detail['주문가능금액'] > buy_price:
                        if cnt_limit > self.count_my_stocks():
                            print(desc)
                            logging.info(desc)

                            buy_price = self.ats.get_tick_price(code, buy_price, -2) # 2틱 아래것을 구매한다.
                            if is_available_trading:
                                self.ats.set_order(self.ats.account_num, code, "신규매수", buy_cnt, buy_price, "지정가") # "시장가")
                                sleep_ms(500)       #  과부하방지
                            else:
                                logging.info('{}({}) : 매수 시간이 아닙니다..'.format(name, code))
                        else:
                            # print('{} : 매수 수량 제한 {} 개를 초과 하였습니다.'.format(text, cnt_limit))
                            logging.error('{}({}) : 매수 수량 제한 {} 개를 초과 하였습니다.'.format(name, code, cnt_limit))
                    else:
                        # print('{} : 매수({}원) 금액이 부족합니다.'.format(text, format(self._ats.trade_detail['주문가능금액'], ',')))
                        logging.error(
                             '{}({}) : 매수({}원) 금액이 부족합니다.'.format(name, code, format(self._ats.trade_detail['주문가능금액'], ',')))


        return True

    def _trade_process(self, code, trade_stock, config, max_amount, now_str, is_available_trading):
        """
        설정값에 따라서, 자동 매매를 처리한다.
        """

        name = trade_stock[DESC_STOCK]['name']
        price = 0 # d_f.close.values[-1]  # 현재가
        cnt = 0  # 매수/매도 수량
        b_buy_trading = False  # 매수 ?
        desc = ''
        d_f = {}

        ####################################################
        # 거래중인 종목, 매도 모드
        ####################################################
        if code in self.ats.account_stocks:
            account_stock = self.ats.account_stocks[code]

            ## ban ?
            if 'ban' in config['sell'] and code in config['sell']['ban']:
                print('==> ban(sell) : {} ({}) '. format(name, code))
            else:
                # 자동매매 ?
                if '자동매매' in account_stock and account_stock['자동매매']:
                    # 자동매매 & 보유수량 & 미체결수량 검사
                    if  (account_stock['미체결수량'] <= 0) and account_stock['보유수량'] > 0:

                        # 손절 자동매매
                        b_sell_trading, cnt, price, desc = self._stoploss_trade(code, name, account_stock, config)

                        # 손절매가 없으면, 매매 방식에 따라서 진행
                        if b_sell_trading is False \
                            and '매매방식' in account_stock \
                            and ('매매정보' in account_stock and '매입시간' in account_stock['매매정보']):
                            holding_minutes = int(config['sell']['holding-limit']) if 'holding-limit' in config['sell'] else 5
                            now = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            diff_time = time_diff(account_stock['매매정보']['매입시간'], now)
                            buy_min = diff_time / 60 # 86400.0 시간으로 변경

                            # 매수 후 최소 시간(5분)을 지켜본다.
                            if buy_min > holding_minutes:
                                func_method_idx = account_stock['매매방식']
                                if func_method_idx in self._trade_func_method['methods']:
                                    func_trade = self._trade_func_method['methods'][func_method_idx]['func']
                                    method = self._trade_func_method['methods'][func_method_idx]

                                    # 사용자 정의 트래이딩 실행한다.
                                    if func_trade is not None and callable(func_trade):
                                        b_sell_trading, cnt, price, desc = func_trade(code, name, account_stock, trade_stock, method, config, max_amount, now_str)

                        # 매도 and && 미체결수량 <= 0 ??
                        if b_sell_trading:
                            if is_available_trading:
                                print(desc)
                                # print_df(df.tail())

                                logging.info(desc)
                                # logging.debug('\n' + tabulate(df.tail(), headers='keys', tablefmt='psql'))

                                self.ats.set_order(self.ats.account_num, code, "신규매도", cnt, 0, "시장가") 
                                sleep_ms(500)   #  과부하방지
                            else:
                                logging.info('{} - 매도 시간이 아닙니다.'.format(desc))

        ####################################################
        # 매수 모드                       
        ####################################################
        else:
            if 'ban' in config['buy'] and code in config['buy']['ban']:
                print('==> ban(buy) : {} ({}) '. format(name, code))
            else:
                # default trade function
                func_trade = self._trade_func_method['methods'][self._trade_func_method['default']]["func"]
                method = self._trade_func_method['methods'][self._trade_func_method['default']]    

                # 사용자 정의 트래이딩 실행한다.
                if func_trade is not None and callable(func_trade):
                    b_buy_trading, cnt, price, desc = func_trade(code, name, None, trade_stock, method, config, max_amount, now_str)

        return b_buy_trading, cnt, price, desc
    
    ############# stoploss 손절매매 #############
    def _stoploss_trade(self, code, name, stock, config):
        """
        트래이딩 이전에 특정 조건에서는 우선적인 손절 매매
        """
        b_sell_trading = False
        text = '{}({})'.format(name, code)
        desc = ''

        cnt = stock['보유수량']
        if cnt > 0:
            price = abs(stock['현재가'])
            v_str = format(price, ',')  # 현재가를 문자로..

            ##### 1. 강제 손절 여부 ####

            # 8% 이하는 100% 손절 매도
            income_rate = float(stock['수익률'])
            if income_rate < config['sell']['full']:
                desc = '===> 손절매도 %s : 현재가 %s, %d개, 손실률 : %.2f' % (text, v_str, cnt, income_rate)
                stock['매도완료'] = 2
                b_sell_trading = True

            # 5% 이하는 50%
            elif income_rate < config['sell']['half']:
                if '매도완료' not in stock:
                    cnt = int((cnt + 1) / 2)
                    desc = '===> 손절매도(1/2) %s: 현재가 %s, 매도: %d주, 손실률 : %.2f' % (text, v_str, cnt, income_rate)
                    stock['매도완료'] = 1
                    b_sell_trading = True

                elif stock['매도완료'] != 1:
                    desc = '===> 손절매도(1/2) %s: 현재가 %s, 매도: %d주, 손실률 : %.2f' % (
                        text, v_str, cnt, income_rate)

            ###### 2. 일정기간 보유기간 #####

            if '매매정보' in stock and '매입시간' in stock['매매정보'] and 'holding-hours' in config['sell']:
                holding_hours = int(config['sell']['holding-hours'])    # 보유기간 
                now = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                diff_time = time_diff(stock['매매정보']['매입시간'], now)
                retention_hour = diff_time / 3600 # 86400.0 시간으로 변경
                if retention_hour > holding_hours:
                    desc = '===> 보유기간 %s: 현재가 %s, 매도: %d주, 손실률 : %.2f, 보유시간 %d(%d 일)' % (
                        text, v_str, cnt, income_rate, retention_hour, retention_hour/24)
                    b_sell_trading = True

            ###### 3. 단계별 스탑로스 ######

            if 'sell' in config and 'stoploss' in config['sell'] \
                and ('use' in config['sell']['stoploss'] and config['sell']['stoploss']['use']) \
                and ('step_stoploss' in config['sell']['stoploss']):
            
                ## // "step_stoploss":"100.0,90.0|70.0,50.0|50.0,30.0|30.0,12.0| 20,8 | 10.0,4.0 |  5.0,2.5 | 3.0,1.5 | 2.5, 1.3| 1.2, 0.6|"
                step_stoploss = parse_stoploss(config['sell']['stoploss']['step_stoploss'])

                buy_price = abs(stock['매입가'])
                high_value = stock['매매정보']['고가']
                low_value = stock['매매정보']['저가'] 

                profit_rate = float(price - buy_price)/float(buy_price) * 100.0
                high_rate = float(high_value - buy_price)/float(buy_price) * 100.0
                log_rate = float(low_value - buy_price)/float(buy_price) * 100.0

                print('==> {}({}) : 현재가 {}, 수익율 {}, 고가비율 {}, 저가비율 {}'.format(
                    name, code, 
                    '{0:1,}'.format(price), 
                    '{0:1,.2f}'.format(income_rate), 
                    '{0:1,.2f}'.format(high_rate), 
                    '{0:1,.2f}'.format(log_rate)
                ))

                # 단계별 stoploss 실행한다.
                for stoploss in step_stoploss:
                    stop_rate = stoploss[0]     # stop ?
                    loss_rate = stoploss[1]     # loss ?

                    # stop loss 기준에 맞는지 ?
                    if (stop_rate < high_rate):
                        adjusted_rate = high_rate - (stop_rate - loss_rate)     # 조정된 loss 부분에 대해서 매도 시도
                        if adjusted_rate > profit_rate:
                            desc ='===> sell(step_stoploss : {} ==> 수익율: {}, ({}, {}))'.format(text, '{0:1,.2f}'.format(profit_rate), stop_rate, loss_rate)
                            b_sell_trading = True
                            break  # 구간이탈....

        return b_sell_trading, cnt, price, desc

    def _trade_macd(self, code, name, stock, trade_stock, func_method, config, max_amount, now_str):
        """
        MACD 오실레이서를 이용하여 매수매도 를 진행한다.
        매수 조건 : MACDO > 0
        매도 조건 : MACDO < 0
        """
        b_trading = False
        buy_cnt = 0
        price = 0
        text = '{}({})'.format(name, code)
        desc = ''

        # 일봉 데이터가 있는지 ?
        if NEW_STOCK not in trade_stock:
             self.get_trade_ohlcv(code, trade_stock=trade_stock)
             sleep_ms(500)      # 과부하 방지
                                         # [REALTIME_STOCK] if REALTIME_STOCK in trade_stock else None,
                                         # trade_min=self._trade_min)

        ################################
        # 보유 종목이 아니면, 매수 진행한다.
        ################################
        if stock is None:
            b_trading = False
            buy_cnt = 0

            ## 조건검색으로 받은 주식...
            if CONDITON_STOCK in trade_stock:
                condition_idx = trade_stock[CONDITON_STOCK]['조건코드']
                condition_name = trade_stock[CONDITON_STOCK]['코드명']

                # 조건코드 설정 값을 확인
                key = '{0:03}'.format(int(condition_idx))
                if OPTIONS in config and OPTIONS_CONDITIONS in config[OPTIONS] \
                    and key in config[OPTIONS][OPTIONS_CONDITIONS] \
                    and OPTIONS_CONDITIONS_CHECK in config[OPTIONS][OPTIONS_CONDITIONS][key] \
                    and config[OPTIONS][OPTIONS_CONDITIONS][key][OPTIONS_CONDITIONS_CHECK]:

                    # 시간 설정값을 읽어 들인다.
                    condition_cfg = config[OPTIONS][OPTIONS_CONDITIONS][key]
                    start_time = condition_cfg[OPTIONS_CONDITIONS_START]
                    end_time = condition_cfg[OPTIONS_CONDITIONS_END]
                    now_time = dt.datetime.now().strftime('%H:%M:%S')

                    # 구매가격....
                    if  end_time > now_time and now_time > start_time:
                        #### 일별 MACD 양수 일때만 매수  
                        if OHLC_DAILY in trade_stock and trade_stock[OHLC_DAILY] is not None:
                            df = util.get_macd(trade_stock[OHLC_DAILY]).dropna()
                            if len(df) > 10:
                                if '현재가' in trade_stock:
                                    df.at[0, 'close'] = abs(trade_stock['현재가'])            # 현재가 수정
                                if '누적거래량' in trade_stock: 
                                    df.at[0, 'volume']  = abs(trade_stock['누적거래량'])  # 거래량 수정
                                
                                macdo = df.macdo.values

                                ## MACD O
                                if (key=='016' and macdo[-1] > 0) or \
                                    (macdo[-1] > 0 and (macdo[-1] > macdo[-2]) and (macdo[-3] < 0 or macdo[-2] < 0)):
                                    b_trading = True
                                    buy_cnt = 100 
                                    price = INT(condition_cfg[OPTIONS_CONDITIONS_AMOUNT])   # 구매값
                                    desc = '==> 조건구매 : {} : [{} - {}], macd: [{}, {}, {}]'.format(text, condition_idx, condition_name,
                                                '{:,.02f}'.format(macdo[-3]), '{:,.02f}'.format(macdo[-2]), '{:,.02f}'.format(macdo[-1]))
                                    
                                    print('{} - start {}, end {}, now {}'.format(text, start_time, end_time, now_time))
                                    if self.develop_mode:
                                        obv = util.OBV(df.close, df.volume)
                                        obv9_signal = obv.ewm(span=9).mean()  # 9일 (시그널)

                                        df = df.assign(obv=obv, obv9_signal=obv9_signal, obvo=obv-obv9_signal)  # .dropna()
                                        df['date'] = df['date'] + '12000000'
                                        # self.draw_df_cart(text, df[-60:])
                                        print(text)
                                        print_df(df.tail())

        ################################
        # 보유 종목이 있으므로, 매도 처리만 한다.
        ################################
        else:
            cnt = stock['보유수량']
            if cnt > 0:
                price = abs(stock['현재가'])
                buy_price = abs(stock['매입가'])
                v_str = format(price, ',')  # 현재가를 문자로..

                #### MACD ###
                if OHLC_DAILY in trade_stock and trade_stock[OHLC_DAILY] is not None:
                    df = util.get_macd(trade_stock[OHLC_DAILY])
                    if len(df) > 10:
                        if '현재가' in trade_stock:
                            df.at[0, 'close'] = abs(trade_stock['현재가'])            # 현재가 수정
                        if '누적거래량' in trade_stock: 
                            df.at[0, 'volume']  = abs(trade_stock['누적거래량'])  # 거래량 수정

                        macdo = df.macdo.values
                        if macdo[-1] < 0:
                            b_trading = True
                            buy_cnt = cnt 
                            # price = price   # 구매값
                            desc = '==> MACD 매도 : {},  현개가: {},  수량: {}, macdo  [ {}, {}, {} ] '.format(text, price, buy_cnt, 
                                                '{:,.02f}'.format(macdo[-3]), '{:,.02f}'.format(macdo[-2]), '{:,.02f}'.format(macdo[-1]))

                        if self.develop_mode:
                            obv = util.OBV(df.close, df.volume)
                            obv9_signal = obv.ewm(span=9).mean()  # 9일 (시그널)

                            df = df.assign(obv=obv, obv9_signal=obv9_signal, obvo=obv-obv9_signal)  # .dropna()
                            df['date'] = df['date'] + '12000000'
                            # self.draw_df_cart(text, df[-60:])
                            print(text)
                            print_df(df.tail())

        return b_trading, buy_cnt, price, desc
    


        # price = abs(d_f.close.values[-1])  # 현재가
        # desc = ''

        # # 최소 4봉 이상 데이터...
        # df = get_macd(d_f)
        # if len(df) < 4:
        #     return

        # print('%s (%s)' % (name, code))
        # print_df(df.tail())

        # logging.debug('%s (%s)' % (name, code))
        # logging.debug('\n' + tabulate(df.tail(), headers='keys', tablefmt='psql'))
        # return b_buy, buy_cnt, price, desc

        # text = '{}({})'.format(name, code)

        # v_str = format(price, ',')  # 현재가를 문자로..
        # macdo = df.macdo.values
        # close = abs(int(df.close.values[-1]))

        # # 보유/당일거래 종목 매도 우선
        # if stock is None:


        # else:
        #     cnt = stock['보유수량']
        #     stock['MACDO'] = macdo[-1]

        #     if cnt > 0:
        #         bSell = False

        #         # 8% 이하는 100% 손절 매도
        #         income_rate = float(stock['수익률'])
        #         if income_rate < config['sell']['full']:
        #             bSell_str = '===> 손절매도 %s : %d개, 손실률 : %.2f' % (text, cnt, income_rate)
        #             stock['매도완료'] = 2
        #             bSell = True

        #         # 5% 이하는 50%
        #         elif income_rate < config['sell']['half']:
        #             if '매도완료' not in stock:
        #                 cnt = int((cnt + 1) / 2)
        #                 bSell_str = '===> 손절매도(1/2) %s: 현재가 %s, 매도: %d주, 손실률 : %.2f' % (text, v_str, cnt, income_rate)
        #                 stock['매도완료'] = 1
        #                 bSell = True
        #             elif stock['매도완료'] != 1:
        #                 bSell_str = '===> 손절매도(1/2) %s: 현재가 %s, 매도: %d주, 손실률 : %.2f, 평가' % (
        #                     text, v_str, cnt, income_rate)

        #         # 시그널 또는 이익실현(realized revenue)
        #         # or and ma20 >= close:  # 1. 시그널 발생  # and obv[-1] > 0
        #         if bSell is False:
        #             if macdo[-1] < 0:
        #                 bSell_str = "==> 매도상황 %s 현재가 %s, 수익률: %.2f" % (text, v_str, income_rate)
        #                 bSell = True

        #             # 이익실현
        #             elif '이익실현' in config['sell'] and stock['수익률'] >= config['sell']['이익실현']:
        #                 bSell_str = "==> 매도상황(이익실현) %s : 현재가 %s, 수익률: %.2f" % (text, v_str, income_rate)
        #                 bSell = True

        #         if bSell:
        #             print(bSell_str)
        #             print_df(df.tail())

        #             logging.info(bSell_str)
        #             logging.debug('\n' + tabulate(df.tail(), headers='keys', tablefmt='psql'))

        #             self._ats.set_order(self._ats.account_num, code, "신규매도", cnt, 0, "시장가")
        #             sleep_ms(500)

        #     else:
        #         # 스팩, 홀딩스는 거래 하지 않는다.
        #         # 특정 시간(종가매매) 이 지났을떼, '당일 실시간 검색결과' 에서 발생된 추전주
        #         if not (name.find('스팩') >= 0 or name.find('홀딩스') >= 0):
        #             if REALTIME_STOCK in trade_stock:
        #                 # 종가매수
        #                 if 'close-tradetime' not in trade_stock \
        #                         and now_str >= config['buy']['close-tradetime'] \
        #                         and (macdo[-1] > 0 and macdo[-2] <= 0):  # and ma20 >= close):
        #                     trade_stock['close-tradetime'] = True
        #                     desc = "==> 실시간 종가 매수 %s: 현재가 %s원" % (text, close)
        #                     b_buy = True

        #                 # 당일 매매중 특정시간이 지난후, 재매수 가능 ?
        #                 else:
        #                     # 60분..
        #                     now = dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        #                     diff = time_diff(now, trade_stock[REALTIME_STOCK])
        #                     if diff >= (60 * 60) and (macdo[-1] > 0 and macdo[-2] <= 0):
        #                         trade_stock[REALTIME_STOCK] = now
        #                         desc = "==> 실시간 재 매수 %s: 현재가 %s원" % (text, close)
        #                         b_buy = True

        # # 비보유 종목 매수 우선
        # else:
        #     # 스팩, 홀딩스는 거래 하지 않는다.
        #     if not (name.find('스팩') >= 0 or name.find('홀딩스') >= 0):
        #         # '실시간 검색결과' 에서 발생된 추천주
        #         if REALTIME_STOCK in trade_stock:
        #             if macdo[-1] > 0 and macdo[-2] <= 0:  # and ma20 >= close:
        #                 desc = "==> 실시간 매수상황 %s, 현재가 %s 원" % (text, v_str)
        #                 b_buy = True
        #         # 전일/ 분석결과에서 나온 추천주일 때..
        #         else:
        #             if macdo[-1] > 0 and macdo[-2] >= 0 and macdo[-3] <= 0:  # and ma20 >= close:
        #                 desc = "==> 매수상황 %s, 현재가 %s 원" % (text, v_str)
        #                 b_buy = True

        # return b_buy, buy_cnt, price, desc

    def do_finish_processing(self, config, now_s):
        """
        자동 트래이드 최종 실행!!!
        """
        ## 1시간마다 hoga 정보를 저장한다.
        if self._last_time[:2] != now_s[:2]:
            hoga_dir = os.path.join(os.getcwd(), 'hoga')
            if os.path.isdir(hoga_dir) is not True:
                os.mkdir(hoga_dir)
            filename = '{}/{}'.format(hoga_dir, dt.datetime.now().strftime('%Y-%m-%d') + 'info.json')
            save_json_file(filename, self.trade_stocks.stocks)

            # 서버로 호가 정보를 보낸다.
            # self.pipe_comm.send(json.dumps(self.trade_stocks.stocks))

    # '주식호가잔량'
    def on_realtime_hoga_jan(self, real_type: str, code: str, name: str, data: dict):
        """
        주식의 실시간 호가 잔량를 구한다.
   
        """ 

        ########## 호가데이터 덤프 저장 ###
        if self.opt.hoga_dump and (code in self.trade_stocks.stocks):
            # 현재가
            data['현재가'] = self.trade_stocks.stocks[code]['현재가'] if '현재가' in self.trade_stocks.stocks[code] else 0

            # 코스피, 코스닥 현상태
            _dashboard = self.ats.dashboard
            data['코스피'] = _dashboard['코스피']
            data['코스닥'] = _dashboard['코스닥']

            hoga_dir = os.path.join(os.getcwd(), 'hoga')
            if os.path.isdir(hoga_dir) is not True:
                os.mkdir(hoga_dir)

            date_s = dt.datetime.now().strftime('%Y-%m-%d')
            hoga_dir = os.path.join(hoga_dir, date_s)
            if os.path.isdir(hoga_dir) is not True:
                os.mkdir(hoga_dir)

            text = '{}({}).json'.format(self.trade_stocks.stocks[code][DESC_STOCK]['name'], code)
            filename = '{}/{}'.format(hoga_dir, date_s + '-' +  text)

            # UTF-8 한글저장
            with open(filename, "a", encoding='UTF-8') as file:
                file.write(json.dumps(data, ensure_ascii=False) + "|")
                file.close()

            # 외부 서버로 호가 정보를 보내 준다.
            if self.client is not None:
                if self.client.send(HOGA, msg=json.dumps(data, ensure_ascii=False)) == False:
                    self.client.reconnect()

        super().on_realtime_hoga_jan(real_type, code, name, data)

    # 주식우선호가
    def on_realtime_hoga_trade(self, real_type: str, code: str, name: str, data: dict):
        """
        실시간 호가 데이터
        """
        super().on_realtime_hoga_trade(real_type, code, name, data)

    ### 외부 서버로 받은 분석 데이터...
    def recv_msg(self, conn, u):
        # msg
        if u[PROTO_CMD] == MSG:
            print(u[PROTO_MSG])
        # text
        elif u[PROTO_CMD] == TXT:
            print(u[PROTO_TXT])
        # hoga
        elif u[PROTO_CMD] == HOGA:
            print(u[PROTO_MSG])

if __name__ == '__main__':
    import argparse
    from ats_version import *

    # Back up the reference to the exceptionhook
    sys._excepthook = sys.excepthook

    # Set the exception hook to our wrapping function
    sys.excepthook = my_exception_hook

    # while True:
    app = QApplication(sys.argv)  # 메인 윈도우를 실행한다.
    app.setStyle('Fusion')

    # argc, argv
    opt = opt_struct()

    if len(sys.argv) > 1:
        argv = sys.argv[1:]

        for idx in range(len(argv)):
            arg = argv[idx]

            if arg.lower() == '-a':
                opt.auto_running = True
            if arg.lower() == '-m':
                opt.trade_min = True
            if arg.lower() == '-d':
                opt.develop_mode = True
            if arg.lower() == '-u':
                opt.ui_only_mode = True
            if arg.lower() == '-o':
                opt.hoga_dump = True
            if arg.lower() == '-s':
                opt.use_external_srv = True
            if arg.lower() == '-n':
                idx += 1
                arg = argv[idx]
                opt.external_server = arg
    # else:
    
    # parser = argparse.ArgumentParser(description='키움증권 AI 주식 트레이딩 시스템 ' + version)
    # parser.add_argument('-a')
    # parser.add_argument('-c')
    # parser.add_argument('-v')
    # # parser.add_argument('-c', '--count')
    # # parser.add_argument('-v', '--verbose', action='store_true')
    # args = parser.parse_args()
    # # print(args.log)

    # print(args.a, args.c, args.v)

    opt.auto_running = True
    opt.develop_mode = True
    opt.hoga_dump = True
    opt.use_external_srv = True

    win = ATSWnd(opt)  # WindowClass의 인스턴스 생성
    win.show()
    sys.exit(app.exec_())  # EventsL
