import csv

print("================================")
print("       AI维修工单系统")
print("================================")
print()


# 创建维修工单
task = {
    "工单编号": "MT-001",
    "设备编号": "P-101",
    "优先级": "高",
    "问题": "振动持续升高",
    "建议检查": "轴承、润滑、联轴器",
    "状态": "待处理"
}


# 写入维修工单文件
with open(
    "maintenance_tasks.csv",
    "w",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "工单编号",
            "设备编号",
            "优先级",
            "问题",
            "建议检查",
            "状态"
        ]
    )

    writer.writeheader()

    writer.writerow(task)


print("AI已经生成维修工单。")
print()

print("工单编号：MT-001")
print("设备编号：P-101")
print("优先级：高")
print("问题：振动持续升高")
print("建议检查：轴承、润滑、联轴器")
print("状态：待处理")

print()
print("工单已保存：maintenance_tasks.csv")
print("================================")