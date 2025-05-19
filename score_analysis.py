
import pandas as pd
import matplotlib.pyplot as plt

# 读取答题记录
df = pd.read_csv("answers.csv")

# 统计每位员工的总答题数、正确题数、正确率
summary = df.groupby(["工号", "姓名"])["是否正确"].agg(["count", "sum"]).reset_index()
summary.columns = ["工号", "姓名", "总题数", "正确题数"]
summary["正确率"] = (summary["正确题数"] / summary["总题数"] * 100).round(2)

# 保存为 Excel
summary.to_excel("results.xlsx", index=False)

# 输出柱状图
plt.figure(figsize=(10, 6))
plt.bar(summary["姓名"], summary["正确率"], color="skyblue")
plt.xticks(rotation=45)
plt.ylabel("正确率 (%)")
plt.title("员工答题正确率分布")
plt.tight_layout()
plt.savefig("score_distribution.png")
plt.show()

print("分析完成，已输出 results.xlsx 和 score_distribution.png")
