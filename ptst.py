class Subscription:
  def __init__(self, title):
    self.title = title
    self.price_monthly = 0
    self.price_yearly = 0
    self.until = None
    self.cc = False

  def CC(self):
    if self.cc == True:
      return "X"
    else:
      return ""

  def Saving(self):
    if self.cc == True:
      return f"{self.price_monthly:>6.2f}"
    else:
      return ""

  def DaysLeft(self):
    if self.until is not None:
      delta = self.until - date.today()
      return delta.days


class SubTrack:
  def __init__(self):
    self.subs = {}
    self.no_active_subscriptions = 0
    self.no_cc_subscriptions = 0
    self.price_monthly_sum = 0
    self.price_yearly_sum = 0
    self.price_yearly_cc_sum = 0
    self.price_monthly_cc_sum = 0

  def add_subscription(self, title, sub):
    if self.is_active(sub):
      subscr = Subscription(title)
      self.no_active_subscriptions += 1
      price_monthly, price_yearly = self.get_price(sub)
      subscr.price_monthly = price_monthly
      subscr.price_yearly = price_yearly
      self.price_monthly_sum += price_monthly
      self.price_yearly_sum += price_yearly
      if 'cc' in sub:
        if sub['cc'] == True:
          subscr.cc = True
          self.no_cc_subscriptions += 1
          self.price_yearly_cc_sum += price_yearly
          self.price_monthly_cc_sum += price_monthly
      if 'until' in sub:
        subscr.until = sub['until']
      self.subs[title] = subscr

  def is_active(self, sub):
    if not 'active' in sub:
      return True
    else:
      if sub['active'] == False:
        return False
    return True

  def get_price(self, sub):
    monthly_price = 0
    yearly_price = 0
    period = 1
    base_price = self.get_base_price(sub)
    if 'period' in sub:
      period = sub['period']
    monthly_price = base_price / period
    yearly_price = base_price / period * 12
    return monthly_price, yearly_price

  def get_base_price(self, sub):
    price = 0
    if 'price' in sub:
      price = sub['price']
    elif 'price_usd' in sub:
      price = sub['price_usd'] * self.get_usd_eur_rate()
    return price

  def get_usd_eur_rate(self):
    return 0.9382

  def print_summary(self):
    self.__print_header()
    print(f"Active subscriptions: {self.no_active_subscriptions}")
    print(f"    CC subscriptions: {self.no_cc_subscriptions}")
    print(f"  Sum monthly prices: {self.price_monthly_sum:>6.2f} EUR")
    print(f"   Sum yearly prices: {self.price_yearly_sum:>6.2f} EUR")
    print(f"   Yearly CC savings: {self.price_yearly_cc_sum:>6.2f} EUR")
    print(f"  Monthly CC savings: {self.price_monthly_cc_sum:>6.2f} EUR")
    print("========================================")

  def print_list(self):
    self.__print_header()
    print("List of active subscriptions\n")
    table = Texttable()
    table.set_cols_dtype(['i', 't', 't', 't', 't', 't'])
    table.header(["#", "Name", "Price", "Until", "CC?", "Saving"])
    i = 0
    for sub in self.subs:
      i += 1
      table.add_row([i, self.subs[sub].title, f"{self.subs[sub].price_monthly:>6.2f}",
                     self.subs[sub].until, self.subs[sub].CC(), self.subs[sub].Saving()])
    table.add_row(['', 'SUMMARY Month',
                   f"{self.price_monthly_sum:>6.2f}", '', '', f"{self.price_monthly_cc_sum:>6.2f}"])
    table.add_row(
        ['', 'SUMMARY Year', f"{self.price_yearly_sum:>6.2f}", '', '', f"{self.price_yearly_cc_sum:>6.2f}"])
    table.set_cols_align(['l', 'l', 'r', 'l', 'c', 'r'])
    print(table.draw())

  def print_cc_list(self):
    self.__print_header()
    print("List of CC subscriptions\n")
    table = Texttable()
    table.set_cols_dtype(['i', 't', 't', 't', 'i'])
    table.header(["#", "Name", "Price", "Until", "Days left"])
    i = 0
    ccsubs = [sub for sub in self.subs if self.subs[sub].cc == True]
    for sub in ccsubs:
      i += 1
      table.add_row([i, self.subs[sub].title,
                     f"{self.subs[sub].price_monthly:>6.2f}", self.subs[sub].until, self.subs[sub].DaysLeft()])
    table.add_row(
        ['', 'SUMMARY Month', f"{self.price_monthly_cc_sum:>6.2f}", '', ''])
    table.add_row(
        ['', 'SUMMARY Year', f"{self.price_yearly_cc_sum:>6.2f}", '', ''])
    table.set_cols_align(['l', 'l', 'r', 'l', 'c'])
    print(table.draw())

  def __print_header(self):
    print("========================================")
    print("=== PLAIN TEXT SUBSCRIPTION TRACKER ====")
    print("========================================")


import argparse
import tomllib
from datetime import date, datetime
from texttable import Texttable

st = SubTrack()

parser = argparse.ArgumentParser()
parser.add_argument(
    'filename', help="Path to subscriptions file", default='./subscriptions.toml', nargs="?")
parser.add_argument("-l", "--list", help="List subscriptions",
                    action='store', nargs="*")
parser.add_argument(
    "-cc", help="List cancellation candidates", action='store', nargs="*")
args = parser.parse_args()

with open(args.filename, "rb") as f:
  data = tomllib.load(f)
  data = dict(sorted(data.items()))

  for sub in data:
    st.add_subscription(sub, data[sub])

  if args.list is not None:
    st.print_list()
  elif args.cc is not None:
    st.print_cc_list()
  else:
    st.print_summary()
