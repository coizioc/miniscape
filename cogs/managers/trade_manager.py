""" Helper class to assist with trades """

from threading import Lock
from cogs.helper import items
from cogs.helper import users
from cogs.errors.trade_error import TradeError
from utils.command_helpers import parse_int


class TradeManager():

    def __init__(self):
        self._active_trades = []
        self._active_traders = set()
        self.curr_trade = None
        self.ctx = None
        self.name_member = None
        self.number = None
        self.itemid = None
        self.offer = None
        self.lock = Lock()

    def add_trade(self, ctx, trade):
        # trade is a dictionary consisting of variables user1, user2, item1, amount1, item2, amount2
        # User1, amount1, and item1 correspond to the person initiating the trade and the items being "offered"
        # User2, amount2, and item2 correspond to what User1 requests User2 pays
        with self.lock:
            self.curr_trade = trade
            self.ctx = ctx
            if self.__is_trade_valid():
                self._active_trades.append(trade)
                self.__add_active_traders()

            # Finish off this trade,reset out variables
            self.curr_trade = None
            self.ctx = None
            self.name_member = None
            self.number = None
            self.itemid = None
            self.offer = None

    def __is_trade_valid(self):
        # Make sure our second user (the recipient of the items) is a real user here
        name = self.curr_trade['user2']
        for member in self.ctx.guild.members:
            if name.lower() in member.name.lower():
                self.name_member = member
                break
        else:
            raise TradeError(f'{name} not found in server.')

        # Check if either user is an Ironman
        if True in users.read_user_multi(self.curr_trade['user1'],
                                         self.name_member.id,
                                         key=users.IRONMAN_KEY):
            raise TradeError('Ironmen Cannot trade')

        # Make sure our second user (the recipient of the items) is a real user here
        name = self.curr_trade['user2']
        for member in self.ctx.guild.members:
            if name.lower() in member.name.lower():
                self.name_member = member
                break
        else:
            raise TradeError(f'{name} not found in server.')

        # Make sure they actually provided a number
        try:
            self.number = int(self.curr_trade['amount1'])
            if self.number < 0:
                raise ValueError
        except ValueError:
            raise TradeError(f'{self.curr_trade["amount1"]} is not a valid number.')



        # Check that the other one is a number too
        try:
            self.offer = parse_int(self.curr_trade['amount2'])
        except ValueError:
            raise TradeError(f'{self.curr_trade["amount2"]} is not a valid offer.')

        # Make sure the item is valid
        try:
            self.itemid = items.find_by_name(self.curr_trade['item1'])
        except KeyError:
            raise TradeError(f'{self.curr_trade["item1"]} is not a valid item.')

        # Make sure user actually has the item and quantity
        if not users.item_in_inventory(self.curr_trade['user1'],
                                       self.itemid,
                                       self.number):
            raise TradeError(f'You do not have {items.add_plural(self.number, self.itemid)} '
                             f'in your inventory.')

        # Check that it's tradeable
        if not items.is_tradable(self.itemid):
            raise TradeError(f'You can not trade this item. ({items.get_attr(itemid)})')

        # Check user2 has enough coins
        if not users.item_in_inventory(self.name_member.id, "0", self.offer):
            raise TradeError(f'{get_display_name(name_member)} does not have '
                             f'enough gold to buy this many items.')

        # Check that neither user is trading
        if not self._active_traders.isdisjoint({self.curr_trade['user1'],
                                                self.name_member.id}):
            raise TradeError("Each user can only have one active trade at a time")

        # Check that the user isn't him/herself
        if self.curr_trade['user1'] == self.name_member.id:
            raise TradeError("You cannot trade with yourself.")


        return True

    def __add_active_traders(self):
        self._active_traders.add(self.curr_trade['user1'])
        self._active_traders.add(self.name_member.id)

    def reset_trade(self, trade, user1, user2):
        with self.lock:
            self.__remove_active_traders(user1, user2)
            self._active_trades.remove(trade)

    def __remove_active_traders(self, user1, user2):
        self._active_traders.remove(user1)
        self._active_traders.remove(user2)

