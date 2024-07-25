import numpy as np


# パラメータの範囲指定
upper_limit_range = (1.01, 1.20)
lower_limit_range = (0.90, 0.99)
steps = 0.01

min_data_points = 30

# パラメータの組み合わせ
upper_limits = np.round(np.arange(upper_limit_range[0], upper_limit_range[1] + steps, steps), 2).tolist()
lower_limits = np.round(np.arange(lower_limit_range[0], lower_limit_range[1] + steps, steps), 2).tolist()

# 移動平均の期間
short_term_window = 5
long_term_window = 10