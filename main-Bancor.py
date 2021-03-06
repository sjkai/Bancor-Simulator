from smartToken import *
from customers import *
from market import *
import random
import numpy as np
import sys
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab

# the Bancor Market has to be sychronized in every different time slot
def sychronizeMarket(market, timeSlot):
    market.sychronize(timeSlot)

TimeSlotNum = 1000
for bouncingInterval in [50, 200]:
    for bouncingRange in [5.0, 10.0, 20.0]:
        for custNum in [500, 2000]:
            for sigma in [0.01, 0.1, 1]:
                            
                # the seeds of pseudo-random numbers
                mySeeds = [0,1,2,3,4,5,6,7,8,9]

                All_TXNUM = 0
                ALL_CANCELEDNUM = 0
                ALL_SLIP = 0
                ALL_MEDIUMSLIP = 0
                ALL_HUGESLIP = 0

                for mySeed in mySeeds:
                    np.random.seed(mySeed)
                    # issue a new smart token
                    initIssue = 3000000
                    CRR = 0.2
                    KennyCoin = Smartcoin(name='Kenny',reservetokenName='ETH',initCRR=0.2, initPrice=1,initIssueNum=initIssue)

                    # create two different markets
                    MyBancorMarket = BancorMarket(smartToken = KennyCoin)

                    print 'T:',bouncingInterval, 'R:', bouncingRange, 'Nc:', custNum, 'sig:', sigma, 'seed:', mySeed, 'processing...'

                    '''
                    First of all, we initialize the customer's tokenBalance and reserveBalance 
                    by Gaussian distributed random number (mu = 200, sigma = 0.1)
                    '''
                    custInitReserveBalance_mu = 200
                    custInitTokenBalance_mu = 200
                    custInitReserveBalance_list = np.random.normal(custInitReserveBalance_mu, 0.1, custNum) # 0.5 is sigma
                    custInitTokenBalance_list = np.random.normal(custInitTokenBalance_mu, 0.1, custNum) # 0.5 is sigma

                    if sum(custInitTokenBalance_list) > (initIssue * (1 - CRR)):
                        print 'ERROR, too many init smart tokens holding by customers.'
                        sys.exit(0)

                    custList = []
                    # here we name single customer as Joe. And every customer is initialized with 
                    # random value of token balance as well as reserve balance.
                    for i in range(custNum):
                        Joe = Customer(smartToken = KennyCoin, market = MyBancorMarket, 
                                        tokenBalance = int(custInitTokenBalance_list[i]), 
                                        reserveBalance = int(custInitReserveBalance_list[i]))
                        custList.append(Joe)

                    # cashTracker records custmers' cash
                    # cashTracker = []
                    # priceTracker records the change of the smart token's price in Bancor market
                    priceTracker = []
                    # transaction tracker records the transations' number in each time slot
                    txTracker = []
                    # canceled transaction tracker records the canceled transactions' number in each time slot
                    canceledTxTracker = []

                    for j in range(TimeSlotNum):
                        # Sychronize the market
                        sychronizeMarket(MyBancorMarket, j)

                        # we assume that in every time slot, all customers change their valuation
                        currentMarketPrice = MyBancorMarket.getCurrentPrice()
                        if (j > 0) and (j % bouncingInterval == 0):
                            ''' 
                            We assume the valuation_mu is generated by random, which denotes the mean valuation
                            of customers when the good or bad news comes into market on a certain time slot,
                            which is divided by bouncing interval.
                            '''
                            valuation_mu = random.uniform(currentMarketPrice/bouncingRange, currentMarketPrice*bouncingRange)
                        else:
                            valuation_mu = currentMarketPrice

                        custValuation_list = np.random.normal(valuation_mu, sigma, custNum)
                        for i in range(custNum):
                            if custValuation_list[i] < 0:
                                # Customer does not want to sell their token in free. 
                                # Here we give them a small valuation when valuation < 0
                                custList[i].changeValuation(0.001*currentMarketPrice)
                            else:
                                custList[i].changeValuation(custValuation_list[i])

                        '''
                        In every time slot, record the information of this time slot in the market, 
                            such as Price, transactionNum and cancled Tx Num of this time slot
                        '''
                        priceTracker.append(KennyCoin.getPrice())
                        txTracker.append(MyBancorMarket.getTransactionNum())
                        canceledTxTracker.append(MyBancorMarket.getCanceledTransactionNum())

                        # show some information in terminal
                        # print ('In time slot:'+str(j)+' | '+str(MyBancorMarket.getTransactionNum())+
                        #     ' happens. And '+str(MyBancorMarket.getCanceledTransactionNum())+' transactions are canceled.')

                    # '''Plotting'''

                    # # Figure about price changing
                    # pricePlot = []
                    # myX_P = []
                    # for j in range(TimeSlotNum):
                    #     pricePlot.append(priceTracker[j])
                    #     myX_P.append(j)
                    # x_P = np.asarray(myX_P)
                    # y_P = np.asarray(pricePlot)
                    # plt.plot(x_P, y_P, 'o-',color = 'navy', alpha = 0.8)
                    # plt.title('Price Change For Bancor Market',fontsize = 25)
                    # plt.xlabel('Time Slot #',fontsize = 15)
                    # plt.ylabel('Price of Smart Token', fontsize = 15)
                    # plt.savefig('Figures/Bancor/Price-'+str(TimeSlotNum)+'BI-'+str(bouncingInterval)+
                    #     'BG-'+str(bouncingRange)+'CN-'+str(custNum)+'Sig-'+str(sigma)+'Seed-'+str(mySeed)+'.pdf', bbox_inches='tight')
                    # plt.close()

                    # # Figure about transactions
                    # txPlot = []
                    # myX_T = []
                    # for j in range(TimeSlotNum):
                    #     txPlot.append(txTracker[j])
                    #     myX_T.append(j)

                    # x_T = np.asarray(myX_T)
                    # y_T = np.asarray(txPlot)
                    # plt.plot(x_T, y_T, 'o-',color = 'navy', alpha = 0.8)
                    # plt.title('Transaction Num For Bancor Market',fontsize = 25)
                    # plt.xlabel('Time Slot #',fontsize = 15)
                    # plt.ylabel('Transaction #', fontsize = 15)
                    # plt.savefig('Figures/Bancor/Transactions-'+str(TimeSlotNum)+'BI-'+str(bouncingInterval)+
                    #     'BG-'+str(bouncingRange)+'CN-'+str(custNum)+'Sig-'+str(sigma)+'Seed-'+str(mySeed)+'.pdf', bbox_inches='tight')
                    # plt.close()

                    # # Figure about canceled transactions
                    # canceledTxPlot = []
                    # myX_C = []
                    # for j in range(TimeSlotNum):
                    #     canceledTxPlot.append(canceledTxTracker[j])
                    #     myX_C.append(j)

                    # x_C = np.asarray(myX_C)
                    # y_C = np.asarray(canceledTxPlot)
                    # plt.plot(x_C, y_C, 'o-',color = 'navy', alpha = 0.8)
                    # plt.title('Canceled Transaction Num For Bancor Market',fontsize = 25)
                    # plt.xlabel('Time Slot #',fontsize = 15)
                    # plt.ylabel('Canceled Transaction #', fontsize = 15)
                    # plt.savefig('Figures/Bancor/CanceledTx-'+str(TimeSlotNum)+'BI-'+str(bouncingInterval)+
                    #     'BG-'+str(bouncingRange)+'CN-'+str(custNum)+'Sig-'+str(sigma)+'Seed-'+str(mySeed)+'.pdf', bbox_inches='tight')
                    # plt.close()

                    # File about transactions counting
                    fw_trax = open('Result/Bancor/Tx_T-'+str(TimeSlotNum)+'BI-'+str(bouncingInterval)+
                        'BG-'+str(bouncingRange)+'CN-'+str(custNum)+'Sig-'+str(sigma)+'Seed-'+str(mySeed)+'.txt', 'w')
                    fw_trax.write('All_Tx:'+'\t'+str(sum(txTracker))+'\tCanceled:'+'\t'+str(sum(canceledTxTracker)))
                    All_TXNUM += sum(txTracker)
                    ALL_CANCELEDNUM += sum(canceledTxTracker)
                    fw_trax.close()

                    # File about price slipping
                    priceSlip = 0
                    mediumPriceSlip = 0
                    hugePriceSlip = 0
                    for j in range(TimeSlotNum - 1):
                        if priceTracker[j+1] < priceTracker[j]:
                            priceSlip += 1
                            if priceTracker[j+1] < 0.95 * priceTracker[j]:
                                mediumPriceSlip += 1
                                if priceTracker[j+1] < 0.8 * priceTracker[j]:
                                    hugePriceSlip += 1
                        else:
                            continue
                    fw_slip = open('Result/Bancor/Slip_T-'+str(TimeSlotNum)+'BI-'+str(bouncingInterval)+
                        'BG-'+str(bouncingRange)+'CN-'+str(custNum)+'Sig-'+str(sigma)+'Seed-'+str(mySeed)+'.txt', 'w')
                    fw_slip.write('Slip:'+'\t'+str(priceSlip)+'\tMedium-slip:'+'\t'
                        +str(mediumPriceSlip)+'\tHuge-slip:'+'\t'+str(hugePriceSlip))
                    ALL_SLIP += priceSlip
                    ALL_MEDIUMSLIP += mediumPriceSlip
                    ALL_HUGESLIP += hugePriceSlip
                    fw_slip.close()

                avg_All_TXNUM = All_TXNUM / float(len(mySeeds))
                avg_ALL_CANCELEDNUM = ALL_CANCELEDNUM / float(len(mySeeds))
                Canceled_TX_Ratio = avg_ALL_CANCELEDNUM / avg_All_TXNUM

                avg_ALL_SLIP = ALL_SLIP / float(len(mySeeds))
                avg_ALL_MEDIUMSLIP = ALL_MEDIUMSLIP / float(len(mySeeds))
                avg_ALL_HUGESLIP = ALL_HUGESLIP / float(len(mySeeds))

                Slip_Ratio = avg_ALL_SLIP / float(TimeSlotNum)
                MediumSlip_Ratio = avg_ALL_MEDIUMSLIP / float(TimeSlotNum)
                HugeSlip_Ratio = avg_ALL_HUGESLIP / float(TimeSlotNum)

                fw_statistic = open('Figures/Bancor/'+str(bouncingInterval)+
                        'BG-'+str(bouncingRange)+'CN-'+str(custNum)+'Sig-'+str(sigma)+'.txt','w')
                fw_statistic.write(str(avg_All_TXNUM)+'\t'+str(avg_ALL_CANCELEDNUM)+'\t'+str(Canceled_TX_Ratio)
                    +'\t'+str(avg_ALL_SLIP)+'\t'+str(avg_ALL_MEDIUMSLIP)+'\t'+str(avg_ALL_HUGESLIP)+'\t'
                    +str(Slip_Ratio)+'\t'+str(MediumSlip_Ratio)+'\t'+str(HugeSlip_Ratio))
                fw_statistic.close()

