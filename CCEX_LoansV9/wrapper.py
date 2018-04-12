import urllib
import urllib2
import json
import time
import hmac,hashlib


def createTimeStamp(datestr, tformat="%Y-%m-%d %H:%M:%S"):
    return time.mktime(time.strptime(datestr, tformat))
 
class poloniex:
    def __init__(self, APIKey, Secret):
        self.APIKey = APIKey
        self.Secret = Secret
        
    def post_process(self, before):
        after = before
        if after == None:
            raise TypeError("post_process function")
        # Add timestamps if there isnt one but is a datetime
        if('return' in after):
            if(isinstance(after['return'], list)):
                for x in xrange(0, len(after['return'])):
                    if(isinstance(after['return'][x], dict)):
                        if('datetime' in after['return'][x] and 'timestamp' not in after['return'][x]):
                            after['return'][x]['timestamp'] = float(createTimeStamp(after['return'][x]['datetime']))
                           
        return after
    #retry for errors from extraction, errors from connection, and errors from URL read timeout respectively

    def api_query(self, command, req={}):
        #If connection not made within 0.9s, error made and handled with @rety
        #raises an SSL error if timeout is reached
        url_timeout = 10
        if(command == "returnOrderBook"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command + '&currencyPair=' + str(req['currencyPair'])),timeout=url_timeout)
            return json.loads(ret.read())
        elif(command == "returnLoanOrders"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + command + '&currency=' + str(req['currency'])),timeout=url_timeout)
            return json.loads(ret.read())
        elif(command == "returnMarketTradeHistory"):
            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/public?command=' + "returnTradeHistory" + '&currencyPair=' + str(req['currencyPair'])),timeout=url_timeout)
            return json.loads(ret.read())
        else:
            req['command'] = command
            req['nonce'] = int(time.time()*1000)
#            req['start'] = 1483228800
#            req['end'] = 1492636264
            post_data = urllib.urlencode(req)
            sign = hmac.new(self.Secret, post_data, hashlib.sha512).hexdigest()
            headers = {
                'Sign': sign,
                'Key': self.APIKey
            }

            ret = urllib2.urlopen(urllib2.Request('https://poloniex.com/tradingApi', post_data, headers),timeout=url_timeout)
            jsonRet = json.loads(ret.read())
            return self.post_process(jsonRet)
 
 
    def returnOrderBook (self, currencyPair):
        return self.api_query("returnOrderBook", {'currencyPair': currencyPair})
 
    def returnMarketTradeHistory (self, currencyPair):
        return self.api_query("returnMarketTradeHistory", {'currencyPair': currencyPair})
 
    def returnLoanOrders (self, currency):
        orders = self.api_query("returnLoanOrders", {'currency': currency})
        #Cleanses the data so only offers or nothing can come through, no errors
        if (not orders) or ('offers' in orders):
            return orders
        else:
            print "Not returnLoanOrders output not correct"
            raise urllib2.URLError("x")
        
    def returnBalances(self):
        return self.api_query('returnBalances')
 

    def returnOpenOrders(self,currencyPair):
        return self.api_query('returnOpenOrders',{"currencyPair":currencyPair})
 
 
    def returnTradeHistory(self,currencyPair):
        return self.api_query('returnTradeHistory',{"currencyPair":currencyPair})

    def buy(self,currencyPair,rate,amount):
        return self.api_query('buy',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

    def sell(self,currencyPair,rate,amount):
        return self.api_query('sell',{"currencyPair":currencyPair,"rate":rate,"amount":amount})

    def cancel(self,currencyPair,orderNumber):
        return self.api_query('cancelOrder',{"currencyPair":currencyPair,"orderNumber":orderNumber})

    def withdraw(self, currency, amount, address):
        return self.api_query('withdraw',{"currency":currency, "amount":amount, "address":address})

    def returnAvailableAccountBalances(self):
        return self.api_query('returnAvailableAccountBalances')
    
    def createLoanOffer(self,currency, amount, duration, autoRenew, lendingRate):
        return self.api_query('createLoanOffer',{"currency":currency, "amount":amount, "duration":duration, "autoRenew":autoRenew, "lendingRate":lendingRate })
    
    def returnOpenLoanOffers(self):
        return self.api_query('returnOpenLoanOffers')
    
    def cancelLoanOffer(self, orderNumber):
        return self.api_query('cancelLoanOffer',{"orderNumber":orderNumber})
    
    def cancelAllOffers(self):
        openLoanOffers = self.returnOpenLoanOffers()
        if "BTC" in openLoanOffers:
            for offer in openLoanOffers["BTC"]:
                self.cancelLoanOffer(offer['id'])
            
    
    