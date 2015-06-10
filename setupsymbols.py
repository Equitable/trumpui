# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 16:02:28 2015

@author: jnm
"""

from trump.orm import SymbolManager
from trump.templating.templates import FFillIT, WorldBankFT, StLouisFEDFT, QuandlFT, GoogleFinanceFT, YahooFinanceFT

sm = SymbolManager()

xiu = sm.create('XIU', overwrite=True)
xiu.add_tags(['ETF', 'iShares'])
xiu.add_meta(Geography='Canada', AssetClass='Equity', MER="0.07")
xiu.set_description("S&P/TSX 60 Index Fund")
xiu.set_units("CAD/unit")
#xiu.add_feed(GoogleFinanceFT('TSE:XIU'))
xiu.add_feed(YahooFinanceFT('XIU.TO'))
xiu.cache()

spy = sm.create('SPY', overwrite=True)
spy.add_tags(['ETF', 'equity'])
spy.set_description("SPDR S&P 500 ETF Trust")
spy.add_meta(Geography='USA', AssetClass='Equity', Index='S&P 500', MER="0.11", CUSIP="78462F103", Exchange="NYSE")
spy.set_units("USD/unit")
spy.add_feed(YahooFinanceFT('SPY'))
spy.cache()

tsla = sm.create('TSLA', overwrite=True)
tsla.add_tags(['ETF', 'equity', 'Company'])
tsla.set_description("Tesla Motor Company Common Stock")
tsla.add_meta(Geography='USA', AssetClass='Equity', Sector='Automotive')
tsla.set_units("USD/unit")
tsla.add_feed(YahooFinanceFT('TSLA'))
tsla.add_feed(GoogleFinanceFT('TSLA'))
#tsla.add_feed(QuandlFT('GOOG/NASDAQ_TSLA', fieldname='Close'))
tsla.cache()

cpi = sm.create('CPI', overwrite=True)
cpi.add_tags(['Consumer', 'Price Index', 'Seasonally Adjusted'])
cpi.set_description("Consumer Price Index for All Urban Consumers: All Items")
cpi.add_meta(Geography='USA', Factor='Inflation', Publisher="BLS")
cpi.set_units("MoM")
cpi.add_feed(StLouisFEDFT('CPIAUCSL'))
cpi.cache()

from pandas.io import wb
wbtickers = wb.search('gdp.*capita.*const')

for wbid, row in wbtickers.iterrows():
    wbi = sm.create(row['id'].replace(".",""), overwrite=True)
    metadf = row['source':'sourceOrganization'].to_frame().to_dict()[wbid]
    
    metadf = {key.replace("source","WB") : value for key, value in metadf.iteritems()}
    wbi.add_tags(row['topics'])
    wbi.add_tags('US')
    wbi.set_description(row['name'])
    wbi.add_meta(**metadf)
    wbi.set_units("NoUnits")
    wbi.add_feed(WorldBankFT(row['id'],'US'))
    
    AnnualIndex = FFillIT('A')
    wbi.set_indexing(AnnualIndex)

    try:
        wbi.cache()
    except:
        print "Couldn't cache {}".format(wbi.name)

sm.finish()