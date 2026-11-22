"""汇率换算小程序：把一笔美元换算成人民币，打印一行结果。

运行方式：python3 starter/hello-fx/convert.py
"""

# 可以改的数都放在最上面。
AMOUNT_USD = 100  # 要换算的金额，单位是美元
USD_TO_CNY = 7.10  # 1 美元换多少人民币。这是一个示例数字，不是真实汇率


def main():
    amount_cny = AMOUNT_USD * USD_TO_CNY
    print(f"{AMOUNT_USD} 美元 ≈ {amount_cny:.2f} 人民币（按 1 美元 = {USD_TO_CNY:.2f} 人民币计算）")


if __name__ == "__main__":
    main()
