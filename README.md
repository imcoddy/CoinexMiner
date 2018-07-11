# CoinexMiner

# 使用须知
1. 本项目没有经过严格测试 目前只在cdybch交易对测试过
2. 交易挖矿有风险
3. 请先小额测试
4. 刚开始使用前 请观察程序执行情况 确定安全 再让它自己跑
5. 本项目由python实现 支持linux macos windows


# 交易策略

1. 查询 余额 cdy bch  难度 cet/h cet价格
2. 检测最近成交 浮动不超过 设定值
3. 检查盘口 如果有空间(买一卖一超过最小 价格单位) 取部分 cdy持有量 
4. 同时 下单买卖 bid_ask_spread 是0 就是 自己和自己成交 如果是 0.1就是 买卖 差千分之1 挂单
5. 检查 两个 order成交情况

	都成交了 继续刷
	只有一个成交 等待 十分钟 还是没成交 跳到1

6. 统计交易量 手续费消耗 每小时 平衡一次消耗的 cdy 和 bch

7. 检测难度 如果已挖到的cet达到 难度的95% 则等待下个小时



# 参数说明

coinex_api_id="xxxx"
机器人密钥id(不要泄漏给他其他人)

coinex_api_key="xxx"
机器人密钥key(不要泄漏给他其他人)

partial_ratio = 0.1
每单的仓位比例 0.1 就是 10%的仓位比例 减少该值 可以减少被套的资金量 但是挖矿速度也会下降

bid_ask_spread = 0 
买单卖单差价 百分比 0就是 原价 自己买自己卖 0.1 就是相差千分之1

wave_ratio = 1
最近成交波动方差 1就是 最近成交价格浮动 小于1% 减小该值可以减少被套风险 但是挖矿速度会下降

market = "CDYBCH"
挖矿交易对 全大写 也可以是 "BTCUSDT" 等等

goods = "CDY"
交易对商品 也可以是 "BTC" 等等 请注意和market对应

money = "BCH"
交易对计价币种 也可以是 "USDT" 等等 请注意和market对应


# 快速开始

1. 安装python3
	https://www.python.org/downloads/
2. 安装的时候 选择添加到系统path

3. 调整 config-example.py 里面的配置参数 (注意 输入的字符全是英文 不要有中文标点符号)

4. 将 config-example.py 改名 config.py

5. 
	打开控制台 输入 python main.py 回车
	windows 平台也可以直接双击 main.py 运行

6. crtl-c 停止运行

7. python balance_cost.py 手动平衡消耗的手续费(程序主动退出或者异常退出后使用)


# 问题反馈
1. 通过github的 issues 提交
2. 通过wechat联系我 wechat_id: kenshin1987
3. 通过telegram http://t.me/bitcoin_faith


# 免责声明
 本项目是公益性质 不搞收费版 不搞会员制 纯属coinex爱好者 互相帮助
 由本程序带来的收益或者亏损都和项目作者没有关系

# 打赏

如果你觉得本项目对你有用
请打赏bch
1QCBhad9pegNenYGbtYYC9mkwZpEUMB3tP
我会继续完善下去










