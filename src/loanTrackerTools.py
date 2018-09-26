import time
import traceback

def checkLoanOrdersSeq(LoanOrders):
    if LoanOrders:
        previousRate = LoanOrders['offers'][0]['rate']
        for offer in LoanOrders['offers']:
            if offer['rate'] < previousRate:
                raise Exception('LoanOrder order extraction is not in sequence')
            else: previousRate = offer['rate']

class restartException(Exception):
    pass
         
def retryDK (func, tries=1, err=None,delay=1,logger=False,*args, **kwargs):
    for x in range(tries):
        try:
            return func(*args,**kwargs)
        except err:
            if logger:            
                print "%s, trying again, try number:%i out of %i. Sleeping for %i seconds "% (err,x+1, tries,delay)
            time.sleep(delay)
    print "URL error, exceeded maximum number of attempts for function: "+func.__name__
    print traceback.format_exc()
    raise restartException("Restart!")           


def cliffFinder(allOrders,maxDepth):
    if not allOrders:
        return 1.0
    usedOffers = []
    currencyCount = 0.0
    #Make a shorter array of only offers which fall within the maxDepth
    for offer in allOrders['offers']:
        currencyCount += float(offer['amount'])
        usedOffers.append(offer)
        if (currencyCount >= maxDepth):
            break
    indexToUndercut = 0
    greatestDiscrepency = 0.0
    
    finalRate = float(usedOffers[-1]['rate'])
    startingVolume = 0.0

    for offer in usedOffers[:-1]:
        startingVolume += float(offer['amount'])
        m = (maxDepth-startingVolume)/(finalRate - float(offer['rate']))
        c = startingVolume - (m*float(offer['rate']))
        buildingVolume = 0.0
        for point in usedOffers[usedOffers.index(offer)+1:]:
            expectedVolume = m*float(point['rate']) + c
            discrepency = expectedVolume - (buildingVolume+startingVolume)
            buildingVolume += float(point['amount'])
            if (discrepency>greatestDiscrepency):
                indexToUndercut = usedOffers.index(point)
    return float(usedOffers[indexToUndercut]['rate'])

def analyse_historic_market(currentTimeStamp, historicDataCursor):
    #Length of  seconds used in meandeviation
    analysis_period = 7200

    query = ("SELECT unix_stamp, loan_rate FROM loan_offer_history WHERE unix_stamp > %i")
    historicDataCursor.execute(query %(currentTimeStamp-analysis_period))
    min_datapoints = 360
    if (historicDataCursor.rowcount <= min_datapoints):
        print "Not enough recent datapoints to assess market attractiveness, %i more datapoints required" %(min_datapoints-historicDataCursor.rowcount)
        return False, False
    #Puts the SQL data in to arrays, index 0 is the most recent data
    structured_data = [[],[],[],[]]
    for (unix_stamp,loan_rate) in historicDataCursor:
        #Puts the data in to quartiles of the analysis period
        if (unix_stamp > (currentTimeStamp - (analysis_period*(1.0/4.0)))):
            structured_data[0].append(loan_rate)
        elif (unix_stamp > (currentTimeStamp - (analysis_period*(2.0/4.0)))):
            structured_data[1].append(loan_rate)
        elif (unix_stamp > (currentTimeStamp - (analysis_period*(3.0/4.0)))):
            structured_data[2].append(loan_rate)
        elif (unix_stamp > (currentTimeStamp - (analysis_period*(4.0/4.0)))):
            structured_data[3].append(loan_rate)             
        else:
            raise Exception('Old data made it in to function "good_current_market"')

    #Calculates the weighted mean deviation
    weighted_averages = []
    weighted_deviations = []
    weightingSum = 0
    for quartile in structured_data:
        if not quartile:
            continue
        qWeighting = 4-structured_data.index(quartile)
        weightingSum += qWeighting
        average = sum(quartile)/len(quartile)
        sumDev = 0
        for rate in quartile:
            sumDev += abs(rate - average)
        meanDev = sumDev / len(quartile)
        weightedDev = meanDev * qWeighting
        weightedAv = average * qWeighting
        weighted_deviations.append(weightedDev)
        weighted_averages.append(weightedAv)

    return sum(weighted_averages)/weightingSum, sum(weighted_deviations)/weightingSum

#===============================================================================
# def segment_array (input, largestValue, smallestValue, segmentCount):
#     output = [[]*segmentCount]
#===============================================================================
            
        
        
    

