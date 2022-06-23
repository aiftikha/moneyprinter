# moneyprinter

This is a futures trading bot using tradingview strategy alerts and python-binance wrapper for the Binance REST API and the Flask framework

Takes in tradingview messages in the format:

{
  "action": "{{strategy.order.action}}",
  "ticker": "{{ticker}}"
}

The bot uses your futures balance to buy/sell (action) the asset (ticker), using 95% of your balance at a leverage of 1. Leverage is increased to meet minimum trade quantity values automatically up to a max of 10

Automatic trailing TP at 2% with a callback rate of 0.3%
Stoploss code is added howver it's commented out, feel free to add your own stoploss

The bot will cancel all orders and close all positions before making a new trade
