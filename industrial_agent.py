import csv
from datetime import datetime

from sklearn.ensemble import RandomForestClassifier


print("========================================")
print("        工业泵 AI Agent 完整系统")
print("========================================")
print()


# ==========================================
# 1. 读取泵历史运行数据
# ==========================================

with open(
    "pump_history.csv",
    "r",
    encoding="utf-8-sig"
) as file:

    reader = csv.DictReader(file)
    pump_data = list(reader)


print("① 运行数据读取完成")
print(f"   数据量：{len(pump_data)} 条")
print()


# ==========================================
# 2. 建立健康状态 AI 模型
# ==========================================

X = []
y = []

for row in pump_data:

    X.append([
        float(row["流量"]),
        float(row["压力"]),
        float(row["温度"]),
        float(row["振动"]),
        float(row["功率"])
    ])

    y.append(row["状态"])


health_model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

health_model.fit(X, y)


# ==========================================
# 3. 当前设备数据
# ==========================================

with open("pump_current.csv", "r", encoding="utf-8-sig") as file:
    reader = csv.DictReader(file)
    current_data = next(row for row in reader if row["设备编号"] == "P-101")

current_pump = [[
    float(current_data["流量"]),
    float(current_data["压力"]),
    float(current_data["温度"]),
    float(current_data["振动"]),
    float(current_data["功率"])
]]


# ==========================================
# 4. AI健康诊断
# ==========================================

prediction = health_model.predict(
    current_pump
)[0]

# 工业规则护栏
current_vibration = current_pump[0][3]

if current_vibration >= 5.0:
    prediction = "严重异常"
elif current_vibration >= 4.0 and prediction == "正常":
    prediction = "警告"


print("② AI健康诊断")
print("--------------------------------")
print(f"   当前状态：{prediction}")
print()



# ==========================================
# 5. 当前设备数据
# ==========================================

print("③ 当前设备数据")
print("--------------------------------")
print(f"   流量：{current_pump[0][0]} m3/h")
print(f"   压力：{current_pump[0][1]} bar")
print(f"   温度：{current_pump[0][2]} C")
print(f"   振动：{current_pump[0][3]} mm/s")
print(f"   功率：{current_pump[0][4]} kW")
print()


# ==========================================
# 自动创建维修工单
# ==========================================

if prediction == "严重异常":

    tasks = []

    try:
        with open(
            "maintenance_tasks.csv",
            "r",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)
            tasks = list(reader)

    except FileNotFoundError:
        tasks = []


    # 查找 P-101 最新工单
    latest_status = None

    for row in reversed(tasks):

        if row["设备编号"] == "P-101":
            latest_status = row["状态"]
            break


    # 只有没有未完成工单时，才创建新工单
    if latest_status in [None, "已完成"]:

        max_id = 0

        for row in tasks:

            try:
                number = int(
                    row["工单编号"].replace("MT-", "")
                )

                if number > max_id:
                    max_id = number

            except:
                pass


        new_task_id = f"MT-{max_id + 1:03d}"


        new_task = {
            "工单编号": new_task_id,
            "设备编号": "P-101",
            "优先级": "高",
            "问题": "严重振动异常",
            "建议检查": "轴承、润滑、联轴器",
            "状态": "待处理"
        }


        with open(
            "maintenance_tasks.csv",
            "a",
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

            writer.writerow(new_task)


        print("================================")
        print("        AI自动创建维修工单")
        print("================================")
        print(f"   工单编号：{new_task_id}")
        print("   设备编号：P-101")
        print("   优先级：高")
        print("   问题：严重振动异常")
        print("   建议检查：轴承、润滑、联轴器")
        print("   状态：待处理")
        print()


    else:

        print("   已存在未完成维修工单，本次不重复创建。")
        print()

# ==========================================
# 6. 查找维修工单
# ==========================================

task_id = None
latest_task = None

try:

    with open(
        "maintenance_tasks.csv",
        "r",
        encoding="utf-8-sig"
    ) as file:

        reader = csv.DictReader(file)
        tasks = list(reader)


    # 从后往前寻找 P-101 最新工单
    for row in reversed(tasks):

        if row["设备编号"] == "P-101":

            latest_task = row
            task_id = row["工单编号"]

            break


except FileNotFoundError:

    tasks = []


# ==========================================
# 7. 处理维修工单
# ==========================================

if latest_task is not None:

    print("④ AI读取已有维修工单")
    print("--------------------------------")
    print(f"   工单编号：{task_id}")
    print(f"   工单状态：{latest_task['状态']}")
    print()


else:

    print("④ 没有找到维修工单")
    print("   暂时无法进入维修闭环")
    print()


# ==========================================
# 8. 读取维修结果
# ==========================================

latest_result = None

if task_id is not None:

    try:

        with open(
            "maintenance_results.csv",
            "r",
            encoding="utf-8-sig"
        ) as file:

            reader = csv.DictReader(file)
            results = list(reader)


        # 从后往前寻找对应工单
        for row in reversed(results):

            if row["工单编号"] == task_id:

                # 必须有维修班组字段
                if "维修班组" in row:

                    latest_result = row
                    break


    except FileNotFoundError:

        latest_result = None


# ==========================================
# 9. 显示维修反馈
# ==========================================

if latest_result is not None:

    print("⑤ AI读取维修反馈")
    print("--------------------------------")

    print(
        f"   工单："
        f"{latest_result['工单编号']}"
    )

    print(
        f"   维修结果："
        f"{latest_result['维修结果']}"
    )

    print(
        f"   处理措施："
        f"{latest_result['处理措施']}"
    )

    print(
        f"   维修人员："
        f"{latest_result['维修人员']}"
    )

    print(
        f"   维修班组："
        f"{latest_result['维修班组']}"
    )

    print(
        f"   状态："
        f"{latest_result['状态']}"
    )

    print()


else:

    print("⑤ 没有找到完整维修反馈")
    print("   请确认维修结果中包含维修班组")
    print()


# ==========================================
# 10. AI验证维修效果
# ==========================================

if latest_result is not None:

    before_vibration = 4.2
    with open("pump_after_maintenance.csv", "r", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        after_data = next(row for row in reader if row["设备编号"] == "P-101")
    after_vibration = float(after_data["维修后振动"])

    improvement = (
        (before_vibration - after_vibration)
        / before_vibration
        * 100
    )

# 计算维修前后功率变化
    before_power = 78.0
    after_power = float(after_data["维修后功率"])

    power_saving = before_power - after_power

    power_saving_percent = (
    power_saving
    / before_power
    * 100
    )


    print("⑥ AI验证维修效果")
    print("--------------------------------")

    print(
        f"   维修前振动："
        f"{before_vibration} mm/s"
    )

    print(
        f"   维修后振动："
        f"{after_vibration} mm/s"
    )

    print(
        f"   维修前功率："
        f"{before_power} kW"
    )

    print(
        f"   维修后功率："
        f"{after_power} kW"
    )

    print(
        f"   功率下降："
        f"{power_saving:.1f} kW"
    )

    print(
        f"   功率下降比例："
        f"{power_saving_percent:.1f}%"
    )

    if after_vibration < before_vibration:

        print("   判断：维修有效")

        print(
            f"   振动下降："
            f"{improvement:.1f}%"
        )

        final_status = "维修后状态改善"


    else:

        print("   判断：维修效果不明显")

        final_status = "需要进一步检查"


    print()


else:

    final_status = "等待维修"


# ==========================================
# 11. AI最终判断
# ==========================================

print("⑦ AI最终判断")
print("--------------------------------")

print("   设备：P-101")
print(f"   当前AI状态：{prediction}")
print(f"   维修状态：{final_status}")

print()

# ==========================================
# 12. 保存AI运行日志
# ==========================================

log_data = {
    "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "设备编号": "P-101",
    "流量": current_pump[0][0],
    "压力": current_pump[0][1],
    "温度": current_pump[0][2],
    "振动": current_pump[0][3],
    "功率": current_pump[0][4],
    "AI状态": prediction,
    "工单编号": task_id if task_id is not None else "",
    "维修状态": final_status
}

file_exists = False

try:
    with open("agent_log.csv", "r", encoding="utf-8-sig"):
        file_exists = True
except FileNotFoundError:
    file_exists = False

with open(
    "agent_log.csv",
    "a",
    newline="",
    encoding="utf-8-sig"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=[
            "时间",
            "设备编号",
            "流量",
            "压力",
            "温度",
            "振动",
            "功率",
            "AI状态",
            "工单编号",
            "维修状态"
        ]
    )

    if not file_exists:
        writer.writeheader()

    writer.writerow(log_data)

print("   AI运行日志已保存到 agent_log.csv")
print()
print("========================================")
print("          AI Agent运行完成")
print("========================================")