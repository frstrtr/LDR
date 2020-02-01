# Love-Death-Robots
Robot Killer scrypt

Trade Too Small = 0.0001BTC limit
v2/exchangeRate/list/ = fiat ratio
How to calculate real exchange rate ?

For your needs, you need to check the latest trades where you will also find the price:
file_get_contents($url."trades?market=LTCBTC&limit=1");
Last trade price = Exchange self rate

Limit Price = fee / feeOrganizationPercent * Amount to sell
Spending = Limit Price * Amount to buy

Exchange Fees
NiceHash Exchange has a very simple fee structure with maker and taker fees. Learn more about the difference between taker and maker fees here.
Trade levels are calculated base on your lifetime activity. Once you reach a certain level, you will never go to a higher fee again!
Here is the fee structure:
Trade level |	MAKER FEE |	TAKER FEE
up to 1.000 EUR	0.5%	0.5%
up to 10.000 EUR	0.4%	0.4%
up to 100.000 EUR	0.3%	0.3%
up to 1.000.000 EUR	0.2%	0.2%
up to 10.000.000 EUR	0.1%	0.1%
up to 100.000.000 EUR	0.05%	0.08%
up to 1.000.000.000 EUR	0.04%	0.06%
up to 10.000.000.000 EUR	0.03%	0.05%
up to 100.000.000.000 EUR	0.02%	0.04%
over 100.000.000.000 EUR	0.01%	0.03%

1. Calculate total trades amount
2. Calculate current fee
3. Calculate minimal order
