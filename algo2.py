import stocks
import matplotlib.pyplot as plt

def norm(data, key_string, r=10):
    d = data[0][key_string]
    for i in range(len(data)):
        data[i][key_string + "_norm"] = round(data[i][key_string]/d,r)

def plot_stock(stock, stock_data, key_string):
    data = [st[key_string] for st in stock_data]
    plt.plot(range(len(stock_data)),data, label = stock)
    # plt.xlabel('Time')
    # plt.ylabel('Prices')
    # plt.title(stock + " Data")
    # plt.show()

def group_by_day(stock_data):
    day = stock_data[0]["insert_time"].day
    group = []
    total = []
    for stock in stock_data:
        if (day != stock["insert_time"].day):
            total.append(group.copy())
            group = []
            day = stock["insert_time"].day
        else:
            group.append(stock)
    return total

def get_data_and_plot(stock, key_string = "price", r = 3):
    stock_data = stocks.get_prices(stock)
    if (stock_data == []):
        print("No Data for " + stock)
        return
    norm(stock_data, key_string, r)
    grouped = group_by_day(stock_data)
    plot_stock(stock, stock_data, key_string + "_norm")
    return grouped, stock_data

def plot_stock_by_day(stock, key_string = "price", r = 3):
    stock_data = stocks.get_prices(stock)
    if (stock_data == []):
        print("No Data for " + stock)
        return
    grouped = group_by_day(stock_data)
    for group in grouped:
        norm(group, key_string, r)
        plot_stock(stock, group, key_string + "_norm")
    return grouped

stock_names = [x["name"] for x in stocks.get_all_stocks()]
# all_data = []
# for stock in stock_names:
#     all_data.append(get_data_and_plot(stock))
# axes = plt.gca()
# axes.set_ylim([0.8,1.2])

for stock in stock_names:
    plot_stock_by_day(stock)
    plt.title(stock + " Day by Day")
    plt.show()
