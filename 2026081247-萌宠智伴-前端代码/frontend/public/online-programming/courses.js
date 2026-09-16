// Python practice data for all five courses.
const courseCatalog = {
  "ml": {
    "title": "机器学习算法",
    "headline": "用代码，探索模型如何预测。",
    "description": "从线性回归到近邻与决策树，实践机器学习的基本方法。",
    "language": "Python",
    "tasks": [
      {
        "name": "线性预测",
        "title": "实现线性回归预测",
        "goal": "根据已给定参数计算 y = kx + b。",
        "background": "模型已经给出斜率和截距，用它预测一个新输入的结果。本题不进行参数训练。",
        "requirements": [
          "输入三个整数 x、k、b，以空格分隔。",
          "输出 k × x + b。"
        ],
        "example": "4 3 2",
        "expected": "14",
        "starter": "x, k, b = map(int, input().split())\n\n# TODO：根据已给定参数计算 y = kx + b。\n",
        "hints": [
          "确认三个输入的顺序。",
          "预测值由乘法和加法组成。",
          "计算 k * x + b，并用 print 输出。"
        ],
        "tests": [
          [
            "4 3 2",
            "14"
          ],
          [
            "0 2 5",
            "5"
          ],
          [
            "2 -1 3",
            "1"
          ]
        ],
        "solution": "print(k * x + b)",
        "level": "基础"
      },
      {
        "name": "误差评估",
        "title": "计算平均绝对误差",
        "goal": "用 MAE 评估回归预测的偏差。",
        "background": "比较多组预测值和真实值，了解模型平均偏离多少。",
        "requirements": [
          "每行输入预测值和真实值，至少一行。",
          "计算绝对误差的平均值，固定输出两位小数。"
        ],
        "example": "3 2\n5 2",
        "expected": "2.00",
        "starter": "import sys\npairs = [list(map(int, line.split())) for line in sys.stdin if line.strip()]\n\n# TODO：用 MAE 评估回归预测的偏差。\n",
        "hints": [
          "先求预测值与真实值的差。",
          "使用 abs 取绝对值。",
          "总误差除以 len(pairs)，结果用 格式化输出 f\"{结果:.2f}\"。"
        ],
        "tests": [
          [
            "3 2\n5 2",
            "2.00"
          ],
          [
            "1 1",
            "0.00"
          ],
          [
            "0 1\n0 0\n0 0",
            "0.33"
          ]
        ],
        "solution": "error = sum(abs(p - a) for p, a in pairs) / len(pairs)\nprint(f\"{error:.2f}\")",
        "level": "进阶"
      },
      {
        "name": "最近邻",
        "title": "用 1-NN 判断类别",
        "goal": "按一维距离选择最接近的训练样本。",
        "background": "最近邻分类参考已有样本的标签。本题使用 K = 1，帮助理解 K 近邻的核心思想。",
        "requirements": [
          "第一行是待分类整数 x；后续每行是样本值及标签 0 或 1。",
          "至少一个样本；输出距离 x 最近的样本标签。",
          "距离相同时选择输入顺序靠前的样本。"
        ],
        "example": "6\n2 0\n7 1\n9 0",
        "expected": "1",
        "starter": "import sys\nx = int(input())\nsamples = [list(map(int, line.split())) for line in sys.stdin if line.strip()]\n\n# TODO：按一维距离选择最接近的训练样本。\n",
        "hints": [
          "一维距离是 abs(value - x)。",
          "遍历样本，记录当前最小距离和标签。",
          "只有新距离严格更小时更新，才能保留并列时的第一项。"
        ],
        "tests": [
          [
            "6\n2 0\n7 1\n9 0",
            "1"
          ],
          [
            "5\n4 0\n6 1",
            "0"
          ],
          [
            "2\n2 1",
            "1"
          ]
        ],
        "solution": "distance = float(\"inf\")\nlabel = 0\nfor value, category in samples:\n    d = abs(value - x)\n    if d < distance:\n        distance = d\n        label = category\nprint(label)",
        "level": "进阶"
      },
      {
        "name": "决策树",
        "title": "实现两层决策规则",
        "goal": "用嵌套条件模拟一棵给定的决策树。",
        "background": "按照已确定的规则预测植物类别，体会决策树逐层判断的过程。本题不训练决策树。",
        "requirements": [
          "输入叶片长度和宽度两个非负整数。",
          "长度小于 5 输出 A；否则宽度小于 3 输出 B；其余输出 C。"
        ],
        "example": "6 2",
        "expected": "B",
        "starter": "length, width = map(int, input().split())\n\n# TODO：用嵌套条件模拟一棵给定的决策树。\n",
        "hints": [
          "先判断叶片长度。",
          "仅长度不小于 5 时，再判断宽度。",
          "特别检查长度 5、宽度 3 的边界。"
        ],
        "tests": [
          [
            "6 2",
            "B"
          ],
          [
            "4 8",
            "A"
          ],
          [
            "5 3",
            "C"
          ]
        ],
        "solution": "if length < 5:\n    print(\"A\")\nelif width < 3:\n    print(\"B\")\nelse:\n    print(\"C\")",
        "level": "挑战"
      }
    ]
  },
  "data": {
    "title": "Python数据分析",
    "headline": "用 Python，读懂数据里的规律。",
    "description": "从统计指标到数据筛选，完成一组真实可运行的 Python 练习。",
    "language": "Python",
    "tasks": [
      {
        "name": "平均值",
        "title": "统计每日学习时长",
        "goal": "用列表和求和计算平均值。",
        "background": "输入几天的学习分钟数，计算平均每天投入的时间。",
        "requirements": [
          "输入至少一个非负整数，以空格分隔。",
          "输出平均值，固定保留两位小数。"
        ],
        "example": "20 30 40",
        "expected": "30.00",
        "starter": "values = list(map(int, input().split()))\n# TODO：求平均值并保留两位小数\n",
        "hints": [
          "列表长度就是记录天数。",
          "sum(values) 可计算总时长。",
          "使用格式化输出 f\"{average:.2f}\"。"
        ],
        "tests": [
          [
            "20 30 40",
            "30.00"
          ],
          [
            "0",
            "0.00"
          ],
          [
            "1 2",
            "1.50"
          ]
        ],
        "solution": "print(f\"{sum(values)/len(values):.2f}\")",
        "level": "基础"
      },
      {
        "name": "数据筛选",
        "title": "筛选达标学习记录",
        "goal": "使用列表筛选并统计数量。",
        "background": "计划每天至少学习 30 分钟，统计有多少天达到目标。",
        "requirements": [
          "输入至少一个非负整数，以空格分隔。",
          "输出大于或等于 30 的记录数量。"
        ],
        "example": "20 30 45 10",
        "expected": "2",
        "starter": "values = list(map(int, input().split()))\n# TODO：统计达到 30 分钟的天数\n",
        "hints": [
          "逐项检查记录是否满足 >= 30。",
          "可以使用循环或列表推导式。",
          "注意 30 本身也是达标。"
        ],
        "tests": [
          [
            "20 30 45 10",
            "2"
          ],
          [
            "30",
            "1"
          ],
          [
            "0 10",
            "0"
          ]
        ],
        "solution": "print(sum(1 for value in values if value >= 30))",
        "level": "基础"
      },
      {
        "name": "中位数",
        "title": "寻找一组数据的中位数",
        "goal": "排序后区分奇数和偶数数量。",
        "background": "中位数是有序数据的中间位置，可以帮助理解典型水平。",
        "requirements": [
          "输入至少一个整数，以空格分隔。",
          "奇数项取中间项，偶数项取中间两项的平均值。",
          "固定保留两位小数。"
        ],
        "example": "8 2 4 6",
        "expected": "5.00",
        "starter": "values = sorted(map(int, input().split()))\nn = len(values)\n# TODO：按数据数量计算中位数\n",
        "hints": [
          "必须先排序。",
          "奇数项中间下标是 n // 2。",
          "偶数项中间下标是 n // 2 - 1 和 n // 2。"
        ],
        "tests": [
          [
            "8 2 4 6",
            "5.00"
          ],
          [
            "9 1 3",
            "3.00"
          ],
          [
            "-2",
            "-2.00"
          ]
        ],
        "solution": "median = values[n//2] if n%2 else (values[n//2-1]+values[n//2])/2\nprint(f\"{median:.2f}\")",
        "level": "进阶"
      },
      {
        "name": "数据波动",
        "title": "计算总体方差",
        "goal": "计算离均差平方的平均值。",
        "background": "两组数据平均值相同时，波动程度可能不同。用总体方差衡量离散程度。",
        "requirements": [
          "输入至少一个整数，以空格分隔。",
          "先求平均值，再求 (每项 - 平均值) 的平方和。",
          "除以数据个数 n，固定输出两位小数；本题不是除以 n - 1 的样本方差。"
        ],
        "example": "2 4 6",
        "expected": "2.67",
        "starter": "values = list(map(int, input().split()))\nmean = sum(values) / len(values)\n# TODO：计算总体方差\n",
        "hints": [
          "每项都要减去 mean。",
          "平方用 ** 2。",
          "平方和除以 len(values)，格式化输出。"
        ],
        "tests": [
          [
            "2 4 6",
            "2.67"
          ],
          [
            "5 5",
            "0.00"
          ],
          [
            "1",
            "0.00"
          ]
        ],
        "solution": "variance = sum((v-mean)**2 for v in values)/len(values)\nprint(f\"{variance:.2f}\")",
        "level": "挑战"
      }
    ]
  },
  "sort": {
    "title": "排序算法进阶",
    "headline": "用代码，理解排序的每一步。",
    "description": "从冒泡与插入排序到归并和比较次数，探索排序的过程与效率。",
    "language": "Python",
    "tasks": [
      {
        "name": "冒泡排序",
        "title": "实现冒泡升序排序",
        "goal": "通过相邻比较和交换完成排序。",
        "background": "让较大的数字逐轮移动到右侧，观察冒泡排序的基本过程。",
        "requirements": [
          "输入至少一个整数，以空格分隔。",
          "使用冒泡排序按升序输出，以单个空格分隔。",
          "不要直接使用内置 sort 或 sorted。"
        ],
        "example": "5 2 4 1",
        "expected": "1 2 4 5",
        "starter": "values = list(map(int, input().split()))\n\n# TODO：通过相邻比较和交换完成排序。\n",
        "hints": [
          "两项相邻值顺序错误时交换。",
          "每一轮都可以缩短右侧比较范围。",
          "外层控制轮数，内层比较 values[j] 与 values[j + 1]。"
        ],
        "tests": [
          [
            "5 2 4 1",
            "1 2 4 5"
          ],
          [
            "2 2 -1",
            "-1 2 2"
          ],
          [
            "7",
            "7"
          ]
        ],
        "solution": "for i in range(len(values) - 1):\n    for j in range(len(values) - 1 - i):\n        if values[j] > values[j + 1]:\n            values[j], values[j + 1] = values[j + 1], values[j]\nprint(*values)",
        "level": "基础"
      },
      {
        "name": "插入排序",
        "title": "实现插入升序排序",
        "goal": "将当前元素插入左侧有序区间。",
        "background": "像整理手里的纸牌一样，把每个新元素放到合适的位置。",
        "requirements": [
          "输入至少一个整数，以空格分隔。",
          "使用插入排序升序输出，以单个空格分隔。",
          "不要直接使用内置 sort 或 sorted。"
        ],
        "example": "4 1 3 2",
        "expected": "1 2 3 4",
        "starter": "values = list(map(int, input().split()))\n\n# TODO：将当前元素插入左侧有序区间。\n",
        "hints": [
          "从下标 1 开始，左侧第一项已经有序。",
          "保存当前值，将较大的左侧元素右移。",
          "找到位置后，把保存的值放回去。"
        ],
        "tests": [
          [
            "4 1 3 2",
            "1 2 3 4"
          ],
          [
            "3 3 1",
            "1 3 3"
          ],
          [
            "0",
            "0"
          ]
        ],
        "solution": "for i in range(1, len(values)):\n    value = values[i]\n    j = i - 1\n    while j >= 0 and values[j] > value:\n        values[j + 1] = values[j]\n        j -= 1\n    values[j + 1] = value\nprint(*values)",
        "level": "进阶"
      },
      {
        "name": "有序归并",
        "title": "合并两组有序数据",
        "goal": "用双指针完成归并排序的合并步骤。",
        "background": "归并排序会将两个已经有序的区间合并成本题中的新序列。",
        "requirements": [
          "输入两行已经升序排列的整数，每行至少一项。",
          "合并成升序序列，以单个空格分隔；保留重复值。",
          "不要把拼接结果直接用 sort 或 sorted 排序。"
        ],
        "example": "1 3 5\n2 3 4",
        "expected": "1 2 3 3 4 5",
        "starter": "a = list(map(int, input().split()))\nb = list(map(int, input().split()))\n\n# TODO：用双指针完成归并排序的合并步骤。\n",
        "hints": [
          "分别用一个指针表示两组数据的当前位置。",
          "比较当前位置，将较小项加入结果并移动对应指针。",
          "某组用完后，把另一组剩余项加入结果。"
        ],
        "tests": [
          [
            "1 3 5\n2 3 4",
            "1 2 3 3 4 5"
          ],
          [
            "-2\n0",
            "-2 0"
          ],
          [
            "1 1\n1",
            "1 1 1"
          ]
        ],
        "solution": "i = j = 0\nresult = []\nwhile i < len(a) and j < len(b):\n    if a[i] <= b[j]:\n        result.append(a[i])\n        i += 1\n    else:\n        result.append(b[j])\n        j += 1\nresult.extend(a[i:])\nresult.extend(b[j:])\nprint(*result)",
        "level": "进阶"
      },
      {
        "name": "比较次数",
        "title": "统计冒泡排序的比较次数",
        "goal": "通过计数观察提前结束如何影响实际比较次数。",
        "background": "有序输入可以让冒泡排序提前结束。固定算法规则后，比较不同输入的计算量。",
        "requirements": [
          "输入至少一个整数，以空格分隔。",
          "第 i 轮比较 n - 1 - i 对相邻项，从 i = 0 开始。",
          "每次比较计数加 1；一整轮无交换就停止。仅输出比较次数。"
        ],
        "example": "1 2 3 4",
        "expected": "3",
        "starter": "values = list(map(int, input().split()))\ncomparisons = 0\n\n# TODO：通过计数观察提前结束如何影响实际比较次数。\n",
        "hints": [
          "一项数据不需要比较。",
          "每轮开始把 swapped 设为 False。",
          "只统计相邻元素的大小比较，不统计循环条件判断。"
        ],
        "tests": [
          [
            "1 2 3 4",
            "3"
          ],
          [
            "4 3 2 1",
            "6"
          ],
          [
            "7",
            "0"
          ],
          [
            "2 1 3",
            "3"
          ]
        ],
        "solution": "for i in range(len(values) - 1):\n    swapped = False\n    for j in range(len(values) - 1 - i):\n        comparisons += 1\n        if values[j] > values[j + 1]:\n            values[j], values[j + 1] = values[j + 1], values[j]\n            swapped = True\n    if not swapped:\n        break\nprint(comparisons)",
        "level": "挑战"
      }
    ]
  },
  "project": {
    "title": "AI项目实践",
    "headline": "用数据，检验你的 AI 项目。",
    "description": "从准确率到分类指标与模型选择，完成项目评估的核心步骤。",
    "language": "Python",
    "tasks": [
      {
        "name": "准确率",
        "title": "评估分类模型准确率",
        "goal": "根据预测与真实标签统计正确比例。",
        "background": "一个分类模型已经生成预测，用独立评估数据衡量表现。",
        "requirements": [
          "每行输入预测标签和真实标签，标签均为 0 或 1，至少一行。",
          "输出正确数量除以总数量的百分比，保留两位小数并追加 %。"
        ],
        "example": "1 1\n0 1\n0 0",
        "expected": "66.67%",
        "starter": "import sys\npairs = [list(map(int, line.split())) for line in sys.stdin if line.strip()]\n\n# TODO：根据预测与真实标签统计正确比例。\n",
        "hints": [
          "预测标签与真实标签相等时计为正确。",
          "正确数量除以 len(pairs)，再乘以 100。",
          "用 格式化输出 f\"{结果:.2f}\" 后拼接 %。"
        ],
        "tests": [
          [
            "1 1\n0 1\n0 0",
            "66.67%"
          ],
          [
            "0 1",
            "0.00%"
          ],
          [
            "1 1",
            "100.00%"
          ]
        ],
        "solution": "correct = sum(p == a for p, a in pairs)\nprint(f\"{correct / len(pairs) * 100:.2f}%\")",
        "level": "基础"
      },
      {
        "name": "混淆矩阵",
        "title": "统计二分类混淆矩阵",
        "goal": "区分 TP、FP、TN、FN 四类结果。",
        "background": "准确率无法展示具体错在哪里。统计误报和漏报，为项目改进提供依据。",
        "requirements": [
          "每行输入预测标签和真实标签，均为 0 或 1，至少一行。",
          "以 TP FP TN FN 的顺序输出四个计数，用空格分隔。",
          "TP：预测1真实1；FP：预测1真实0；TN：预测0真实0；FN：预测0真实1。"
        ],
        "example": "1 1\n1 0\n0 0\n0 1",
        "expected": "1 1 1 1",
        "starter": "import sys\npairs = [list(map(int, line.split())) for line in sys.stdin if line.strip()]\n\n# TODO：区分 TP、FP、TN、FN 四类结果。\n",
        "hints": [
          "将预测标签与真实标签组合判断。",
          "准备四个初始值为 0 的计数变量。",
          "注意输出顺序，FP 与 FN 不要混淆。"
        ],
        "tests": [
          [
            "1 1\n1 0\n0 0\n0 1",
            "1 1 1 1"
          ],
          [
            "0 1",
            "0 0 0 1"
          ],
          [
            "1 1\n1 1",
            "2 0 0 0"
          ]
        ],
        "solution": "tp = fp = tn = fn = 0\nfor p, a in pairs:\n    if p == 1 and a == 1:\n        tp += 1\n    elif p == 1:\n        fp += 1\n    elif a == 0:\n        tn += 1\n    else:\n        fn += 1\nprint(tp, fp, tn, fn)",
        "level": "进阶"
      },
      {
        "name": "查准与查全",
        "title": "计算 Precision 和 Recall",
        "goal": "根据计数计算精确率与召回率。",
        "background": "根据项目目标分析误报和漏报，了解两个指标关注的不同方面。",
        "requirements": [
          "输入三个非负整数 TP、FP、FN。",
          "Precision = TP / (TP + FP)，Recall = TP / (TP + FN)。",
          "分母为 0 时本题约定指标为 0；输出两个比例，均保留两位小数，用空格分隔。"
        ],
        "example": "3 1 2",
        "expected": "0.75 0.60",
        "starter": "tp, fp, fn = map(int, input().split())\n\n# TODO：根据计数计算精确率与召回率。\n",
        "hints": [
          "精确率关注预测为正的结果，召回率关注真实为正的样本。",
          "先分别检查两个分母。",
          "输出比例而不是百分比，使用 格式化输出 f\"{结果:.2f}\"。"
        ],
        "tests": [
          [
            "3 1 2",
            "0.75 0.60"
          ],
          [
            "0 0 0",
            "0.00 0.00"
          ],
          [
            "2 0 0",
            "1.00 1.00"
          ]
        ],
        "solution": "precision = tp / (tp + fp) if tp + fp else 0\nrecall = tp / (tp + fn) if tp + fn else 0\nprint(f\"{precision:.2f} {recall:.2f}\")",
        "level": "进阶"
      },
      {
        "name": "模型选择",
        "title": "在预算内选择最佳模型",
        "goal": "组合评估指标与推理耗时进行选择。",
        "background": "部署项目时需要兼顾效果与性能。本题用验证集准确率选模型，不使用最终测试集挑选模型。",
        "requirements": [
          "第一行输入非负整数耗时预算。",
          "后续每行输入准确率百分值（0～100，可含小数）和非负整数耗时，至少一个模型。",
          "从耗时不超过预算的模型中选择准确率最高者，输出从 1 开始的编号。",
          "准确率相同时选耗时更短者；仍相同选靠前者。没有符合预算的模型输出 -1。"
        ],
        "example": "50\n90 60\n88 30\n92 45",
        "expected": "3",
        "starter": "import sys\nbudget = int(input())\nmodels = [list(map(float, line.split())) for line in sys.stdin if line.strip()]\n\n# TODO：组合评估指标与推理耗时进行选择。\n",
        "hints": [
          "先排除耗时大于 budget 的模型。",
          "记录目前最佳的准确率、耗时和编号。",
          "只在准确率更高或同准确率耗时更短时更新。"
        ],
        "tests": [
          [
            "50\n90 60\n88 30\n92 45",
            "3"
          ],
          [
            "0\n90 1",
            "-1"
          ],
          [
            "40\n90 30\n90 20\n90 20",
            "2"
          ]
        ],
        "solution": "best = -1\nfor i, (accuracy, time) in enumerate(models):\n    if time <= budget and (best < 0 or accuracy > models[best][0] or (accuracy == models[best][0] and time < models[best][1])):\n        best = i\nprint(best + 1 if best >= 0 else -1)",
        "level": "挑战"
      }
    ]
  },
  "deep": {
    "title": "深度学习基础",
    "headline": "用代码，理解神经网络。",
    "description": "从神经元计算到简单分类，逐步完成实践。",
    "language": "Python",
    "tasks": [
      {
        "name": "神经元计算",
        "title": "计算一个神经元的输出",
        "level": "基础",
        "goal": "理解输入、权重和偏置，计算 z = x × w + b。",
        "background": "神经元会先对输入进行加权，再加上偏置。本任务只实现激活前的计算，帮助你理解神经网络的基本组成。",
        "requirements": [
          "输入三个整数 x、w、b，以空格分隔。",
          "按照 z = x × w + b 计算并输出结果。"
        ],
        "example": "3 2 1",
        "expected": "7",
        "starter": "x, w, b = map(int, input().split())\n\n# TODO：理解输入、权重和偏置，计算 z = x × w + b。\n",
        "hints": [
          "x 是输入，w 是权重，b 是偏置。",
          "先计算 x * w，再加上 b。",
          "使用 print(x * w + b) 输出结果。"
        ],
        "tests": [
          [
            "3 2 1",
            "7"
          ],
          [
            "0 5 2",
            "2"
          ],
          [
            "2 -3 1",
            "-5"
          ]
        ],
        "solution": "print(x * w + b)"
      },
      {
        "name": "ReLU 激活",
        "title": "为神经元添加 ReLU 激活",
        "level": "基础",
        "goal": "实现 ReLU(z) = max(0, z)，理解激活函数的作用。",
        "background": "激活函数让神经网络能够表达非线性关系。ReLU 会将负数变成 0，非负数保持不变。",
        "requirements": [
          "输入一个整数 z，表示激活前的输出。",
          "如果 z 小于 0，输出 0；否则输出 z。"
        ],
        "example": "-3",
        "expected": "0",
        "starter": "z = int(input())\n\n# TODO：实现 ReLU(z) = max(0, z)，理解激活函数的作用。\n",
        "hints": [
          "需要考虑负数、0 和正数。",
          "使用条件判断或 max(0, z)。",
          "用 print() 输出结果。"
        ],
        "tests": [
          [
            "-3",
            "0"
          ],
          [
            "0",
            "0"
          ],
          [
            "8",
            "8"
          ]
        ],
        "solution": "print(max(0, z))"
      },
      {
        "name": "预测误差",
        "title": "计算模型的均方误差",
        "level": "进阶",
        "goal": "计算均方误差 MSE，衡量预测值与真实值的差距。",
        "background": "训练神经网络时，需要用损失衡量预测的好坏。本任务将每组预测误差平方，再求平均；数值越小，代表这一组预测更接近真实值。",
        "requirements": [
          "每行输入两个整数：预测值和真实值，至少一行。",
          "计算所有样本的平均平方误差。",
          "结果固定保留两位小数，例如 0.00。"
        ],
        "example": "3 2\n5 3",
        "expected": "2.50",
        "starter": "import sys\npairs = [list(map(int, line.split())) for line in sys.stdin if line.strip()]\n\n# TODO：计算均方误差 MSE，衡量预测值与真实值的差距。\n",
        "hints": [
          "每个样本的误差是预测值减去真实值。",
          "平方可以写成 (p - a) ** 2。",
          "除以 len(pairs)，再使用 f\"{loss:.2f}\" 输出。"
        ],
        "tests": [
          [
            "3 2\n5 3",
            "2.50"
          ],
          [
            "4 4\n0 0",
            "0.00"
          ],
          [
            "1 3",
            "4.00"
          ],
          [
            "0 1\n0 0\n0 0",
            "0.33"
          ]
        ],
        "solution": "loss = sum((p - a) ** 2 for p, a in pairs) / len(pairs)\nprint(f\"{loss:.2f}\")"
      },
      {
        "name": "简单分类",
        "title": "搭建一个二分类神经元",
        "level": "挑战",
        "goal": "组合加权求和与阈值判断，完成简化的二分类预测。",
        "background": "将两个输入交给一个神经元。先计算 z = x1 × w1 + x2 × w2 + b，再用 0 作为分类阈值。这是用于理解预测流程的简化模型，不涉及训练过程。",
        "requirements": [
          "输入五个整数 x1、x2、w1、w2、b，以空格分隔。",
          "计算 z；z 大于或等于 0 时输出 1，否则输出 0。",
          "注意 z 等于 0 时也输出 1。"
        ],
        "example": "2 3 1 -1 0",
        "expected": "0",
        "starter": "x1, x2, w1, w2, b = map(int, input().split())\n\n# TODO：组合加权求和与阈值判断，完成简化的二分类预测。\n",
        "hints": [
          "输入分别乘以权重，再相加并加上偏置。",
          "分类条件是 z >= 0。",
          "使用 if / else 和 print() 输出类别。"
        ],
        "tests": [
          [
            "2 3 1 -1 0",
            "0"
          ],
          [
            "1 1 1 1 0",
            "1"
          ],
          [
            "0 0 2 3 0",
            "1"
          ],
          [
            "0 0 2 3 -1",
            "0"
          ]
        ],
        "solution": "z = x1 * w1 + x2 * w2 + b\nprint(1 if z >= 0 else 0)"
      }
    ]
  }
};
