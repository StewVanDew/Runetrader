from tools import realistic_mouse as mouse, realistic_keyboard as keyboard
from classes import orders, items
import datetime
import config
import json
import random


def find_items():
    print("DEBUG: Generating random item list")

    data = json.load(open("./data/items.json", 'r'))
    return [items.Item(item['name']) for item in data if item['members'] == config.membership]


def find_margin(client, item):

    print("DEBUG: Finding margin for item", item.name)

    exchange = client.exchange

    order = place_buy_order(client, item, 1, ['up', 3])

    time = datetime.datetime.now()
    while not exchange.order_completed(order.slot):
        if time < datetime.datetime.today() - datetime.timedelta(hours=1):
            exchange.abort_order(order.slot)
            return

    client.inventory.add(item, 1)
    p1, q1 = exchange.retrieve_items(order.slot)

    order = place_sell_order(client, item, 1, ['down', 3])

    time = datetime.datetime.now()
    while not exchange.order_completed(order.slot):
        if time < datetime.datetime.today() - datetime.timedelta(hours=1):
            exchange.abort_order(order.slot)
            return

    client.inventory.remove(item, 1)
    p2, q2 = exchange.retrieve_items(order.slot)

    return p1, p2


def place_buy_order(client, item, amount, price):
    print("DEBUG: Placing buy order for {0} {1} at {2} gp each".format(amount, item.name, price))

    exchange = client.exchange

    slot = exchange.empty_slots[0]
    exchange.empty_slots = [s for s in exchange.empty_slots if s != slot]

    mouse.all_in_one(*slot.buy_button)

    keyboard.write(item.name)

    mouse.all_in_one(*exchange.first_item)

    if type(price) == list:
        if price[0] == 'up':
            mouse.random_move(*exchange.percent_up_button)
        else:
            mouse.random_move(*exchange.percent_down_button)

        for i in range(price[1]):
            mouse.click()
    else:
        exchange.set_price(price)

    exchange.set_amount(amount)

    exchange.confirm()

    return orders.Order(slot, item)


def place_sell_order(client, item, amount, price):
    print("DEBUG: Placing sell order for {0} {1} at {2} gp each".format(amount, item.name, price))

    exchange = client.exchange

    slot = exchange.empty_slots[0]
    exchange.empty_slots = [s for s in exchange.empty_slots if s != slot]

    mouse.all_in_one(*slot.sell_button)

    inventory_spot = client.inventory.find(item)
    print(inventory_spot)
    mouse.all_in_one(*inventory_spot.coordinates)

    if type(price) == list:
        if price[0] == 'up':
            mouse.random_move(*exchange.percent_up_button)
        else:
            mouse.random_move(*exchange.percent_down_button)

        for i in range(price[1]):
            mouse.click()
    else:
        exchange.set_price(price)

    exchange.set_amount(amount)

    exchange.confirm()

    return orders.Order(slot, item)