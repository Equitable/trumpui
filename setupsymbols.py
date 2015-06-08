# -*- coding: utf-8 -*-
"""
Created on Sat Jun  6 16:02:28 2015

@author: jnm
"""

from trump.orm import SymbolManager
from trump.templating.templates import StLouisFEDFT, QuandlFT, GoogleFinanceFT, YahooFinanceFT

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
tsla.add_feed(QuandlFT('GOOG/NASDAQ_TSLA', fieldname='Close'))
tsla.cache()

tsla = sm.create('CPI', overwrite=True)
tsla.add_tags(['Consumer', 'Price Index', 'Seasonally Adjusted'])
tsla.set_description("Consumer Price Index for All Urban Consumers: All Items")
tsla.add_meta(Geography='USA', Factor='Inflation', Publisher="BLS")
tsla.set_units("MoM")
tsla.add_feed(StLouisFEDFT('CPIAUCSL'))
tsla.cache()

sm.finish()