from wrapper import poloniex
from loanTrackerTools import checkLoanOrdersSeq, cliffFinder, analyse_historic_market, retryDK, restartException
import urllib2
import time
import pymysql
import ssl

while (1):
    try:
        #Account API login and SQL database login
        account = poloniex("ACOUNT DETAILS HAVE BEEN REMOVED!!!","ACOUNT DETAILS HAVE BEEN REMOVED!!!")
        #prepare up mySQL for input
        #dataBase = retry_mysql_connect(host="localhost", port=3306, user="root", passwd="Gowntime6", db="ccetloans")
        dataBase = retryDK(pymysql.connect, 5, pymysql.err.OperationalError,10,True, host="ACOUNT DETAILS HAVE BEEN REMOVED!!!", port=ACOUNT DETAILS HAVE BEEN REMOVED!!!, user="ACOUNT DETAILS HAVE BEEN REMOVED!!!", passwd="ACOUNT DETAILS HAVE BEEN REMOVED!!!", db="ACOUNT DETAILS HAVE BEEN REMOVED!!!")
        cur = dataBase.cursor()
        
        dateTime = time.strftime('%Y-%m-%d %H:%M:%S')
        timeStamp = int(time.time())
        
        #Analyse historic data
        wMean, wDev  = analyse_historic_market(timeStamp,cur)
        loanThreshold = wMean + (0.8*wDev)
        #Retrieve the market data for loan orders and check the sequence is correct
        LoanOrders = retryDK(account.returnLoanOrders,5, (TypeError,urllib2.URLError,ssl.SSLError),1,True,"BTC")
        checkLoanOrdersSeq(LoanOrders)
        #Calculate the rate to invest at given a snapshot of the market
        loanOfferRate = cliffFinder(LoanOrders,1.0)
        #print "Offer Rate: ", loanOfferRate
        #print "wMean: ", wMean
        
        #Removes all open offers and checks the new balance
        LoanOrders = retryDK(account.cancelAllOffers,5, (TypeError,urllib2.URLError,ssl.SSLError),1,True)
        #print "All Offers canceled"
        accBalance = retryDK(account.returnAvailableAccountBalances,5, (TypeError,urllib2.URLError,ssl.SSLError),1,True)
        #Checks if there is any BTC in the acc
        print "accBalance: ", accBalance
        if 'lending' in accBalance:
            accBalanceBTC = float(accBalance['lending']['BTC'])
                #Check I have enough currency in my lending account
            #print "accBalanceBTC: ", accBalanceBTC
            if  accBalanceBTC>= 0.01:
                #Only loan all if there is not enough to split in to two or if the rate is above 30% P.A.
                if (accBalanceBTC < 0.02) or loanOfferRate > 0.000822:
                    offerAmount = accBalanceBTC
                else: offerAmount = accBalanceBTC/2
                #print "Enough BTC in the account"
                if (wMean != False) and (loanOfferRate > loanThreshold):
                    madeOffer = retryDK(account.createLoanOffer,5, (TypeError,urllib2.URLError,ssl.SSLError),1,True,"BTC",str(offerAmount),"2","0",str(loanOfferRate-0.000001))
                    print "--------------------", madeOffer, "--------------------"
                else: print "Not enough data or rate too low"
            else: print "Less than 0.01 BTC left"
        else: print "No BTC left"
    
        cur.execute("""INSERT INTO loan_offer_history (date_time, unix_stamp, loan_rate) VALUES ("%s","%i","%f")"""% (dateTime,timeStamp, loanOfferRate))
        dataBase.commit()
        cur.close()
        dataBase.close()
        print "It is safe to terminate for 10 seconds as of", time.strftime("%H:%M:%S")
        time.sleep(10)
    except restartException:
        continue