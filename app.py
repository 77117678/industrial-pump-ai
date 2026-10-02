import streamlit as st
import pandas as pd
import subprocess
import sys


# ==========================================
# 网页设置
# ==========================================

st.set_page_config(
    page_title="工业泵 AI Agent",
    page_icon="⚙️",
    layout="wide"
)


# ==========================================
# 简单页面样式
# ==========================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .sub-title {
        font-size: 18px;
        opacity: 0.75;
        margin-bottom: 20px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 650;
        margin-top: 15px;
        margin-bottom: 10px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================
# 读取当前设备数据
# ==========================================

data = pd.read_csv(
    "pump_current.csv",
    encoding="utf-8-sig"
)

pump = data.iloc[0]

device_id = str(pump["设备编号"])

flow = float(pump["流量"])
pressure = float(pump["压力"])
temperature = float(pump["温度"])
vibration = float(pump["振动"])
power = float(pump["功率"])


# ==========================================
# AI状态判断
# ==========================================

if vibration >= 5.0:
    status = "严重异常"
elif vibration >= 4.0:
    status = "警告"
elif vibration >= 2.5:
    status = "注意"
else:
    status = "正常"


# ==========================================
# 健康评分
# 注意：目前仍然是原型评分
# ==========================================

vibration_score = max(
    0,
    min(
        100,
        100 - max(vibration - 2.5, 0) / 3.0 * 100
    )
)

temperature_score = max(
    0,
    min(
        100,
        100 - max(temperature - 65, 0) / 15.0 * 100
    )
)

power_score = max(
    0,
    min(
        100,
        100 - max(power - 72, 0) / 13.0 * 100
    )
)

health_score = round(
    vibration_score * 0.60
    + temperature_score * 0.25
    + power_score * 0.15
)


# ==========================================
# 最近维修记录
# ==========================================

latest_repair = None

try:

    repair_data = pd.read_csv(
        "maintenance_results.csv",
        encoding="utf-8-sig"
    )

    device_repairs = repair_data[
        repair_data["设备编号"] == device_id
    ]

    if len(device_repairs) > 0:
        latest_repair = device_repairs.iloc[-1]

except Exception:
    latest_repair = None


# ==========================================
# 维修效果
# ==========================================

before_vibration = None
after_vibration = None
vibration_improvement = None

before_power = None
after_power = None
power_saving = None
power_saving_percent = None

try:

    before_vibration = 4.2
    before_power = 78.0

    after_data = pd.read_csv(
        "pump_after_maintenance.csv",
        encoding="utf-8-sig"
    )

    after_vibration = float(
        after_data.iloc[0]["维修后振动"]
    )

    after_power = float(
        after_data.iloc[0]["维修后功率"]
    )

    vibration_improvement = (
        (before_vibration - after_vibration)
        / before_vibration
        * 100
    )

    power_saving = (
        before_power - after_power
    )

    power_saving_percent = (
        power_saving
        / before_power
        * 100
    )

except Exception:
    pass


# ==========================================
# 左侧菜单
# ==========================================

st.sidebar.title("工业泵 AI Agent")

st.sidebar.caption(
    f"当前设备：{device_id}"
)

menu = st.sidebar.radio(
    "功能菜单",
    [
        "驾驶舱",
        "设备监控",
        "AI诊断",
        "维修工单",
        "能耗分析"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "工业泵 AI Agent · P-101"
)


# ==========================================
# 驾驶舱
# ==========================================

if menu == "驾驶舱":

    st.markdown(
        '<div class="main-title">工业泵 AI Agent 智能驾驶舱</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f'<div class="sub-title">设备：{device_id} · AI监控中心</div>',
        unsafe_allow_html=True
    )

    # --------------------------------------
    # 第一行：状态 + 健康评分
    # --------------------------------------

    col_status, col_health = st.columns(2)

    with col_status:

        st.subheader("P-101 当前状态")

        if status == "正常":

            st.success(
                "🟢 设备正常"
            )

        elif status == "注意":

            st.warning(
                "🟡 设备需要关注"
            )

        elif status == "警告":

            st.warning(
                "🟠 设备警告"
            )

        else:

            st.error(
                "🔴 设备严重异常"
            )

    with col_health:

        st.subheader("设备健康评分")

        if health_score >= 80:

            st.success(
                f"🟢 {health_score} / 100 · 健康状态良好"
            )

        elif health_score >= 60:

            st.warning(
                f"🟡 {health_score} / 100 · 需要关注"
            )

        else:

            st.error(
                f"🔴 {health_score} / 100 · 风险较高"
            )

    # --------------------------------------
    # AI预警
    # --------------------------------------

    st.subheader("AI预警中心")

    if status == "正常":

        st.success(
            f"🟢 当前暂无严重预警 · "
            f"P-101 振动 {vibration:.1f} mm/s"
        )

    elif status == "注意":

        st.warning(
            f"🟡 AI预警：设备需要关注 · "
            f"当前振动 {vibration:.1f} mm/s"
        )

    elif status == "警告":

        st.warning(
            f"🟠 AI预警：振动异常 · "
            f"当前振动 {vibration:.1f} mm/s"
        )

        st.write(
            "建议重点检查轴承、润滑和联轴器。"
        )

    else:

        st.error(
            f"🔴 AI预警：严重振动异常 · "
            f"当前振动 {vibration:.1f} mm/s"
        )

        st.write(
            "建议检查轴承、润滑和联轴器，"
            "并根据现场安全规程决定后续处置。"
        )

    st.divider()

    # --------------------------------------
    # 核心运行参数
    # --------------------------------------

    st.markdown(
        '<div class="section-title">核心运行参数</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:

        st.metric(
            "流量",
            f"{flow:.1f} m³/h"
        )

    with col2:

        st.metric(
            "压力",
            f"{pressure:.1f} bar"
        )

    with col3:

        st.metric(
            "温度",
            f"{temperature:.1f} °C"
        )

    with col4:

        st.metric(
            "振动",
            f"{vibration:.1f} mm/s"
        )

    with col5:

        st.metric(
            "功率",
            f"{power:.1f} kW"
        )

    st.divider()

    # --------------------------------------
    # 30天振动趋势
    # --------------------------------------

    history = pd.read_csv(
        "pump_history.csv",
        encoding="utf-8-sig"
    )

    history["运行时间"] = (
        history["天数"].astype(str)
        + "-"
        + history["小时"].astype(str)
    )

    st.subheader("30天振动趋势")

    chart_data = history[
        ["运行时间", "振动"]
    ].copy()

    chart_data = chart_data.set_index(
        "运行时间"
    )

    st.line_chart(
        chart_data,
        y="振动"
    )

    st.divider()

    # --------------------------------------
    # 底部信息
    # --------------------------------------

    left_col, right_col = st.columns(2)

    with left_col:

        st.subheader("最近一次维修")

        if latest_repair is not None:

            st.success(
                f"工单：{latest_repair['工单编号']}"
            )

            st.write(
                f"维修状态：{latest_repair['状态']}"
            )

            st.write(
                f"维修结果：{latest_repair['维修结果']}"
            )

            st.write(
                f"处理措施：{latest_repair['处理措施']}"
            )

        else:

            st.info(
                "暂无维修记录。"
            )

    with right_col:

        st.subheader("维修效果")

        if (
            vibration_improvement is not None
            and power_saving is not None
        ):

            st.metric(
                "振动下降",
                f"{vibration_improvement:.1f}%"
            )

            st.metric(
                "功率下降",
                f"{power_saving:.1f} kW"
            )

            st.write(
                f"功率变化："
                f"{before_power:.1f} → "
                f"{after_power:.1f} kW"
            )

        else:

            st.info(
                "暂无维修效果数据。"
            )


# ==========================================
# 设备监控
# ==========================================

elif menu == "设备监控":

    st.title("设备实时监控")

    st.caption(
        f"设备：{device_id}"
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "流量",
            f"{flow:.1f} m³/h"
        )

        st.metric(
            "温度",
            f"{temperature:.1f} °C"
        )

        st.metric(
            "振动",
            f"{vibration:.1f} mm/s"
        )

    with col2:

        st.metric(
            "压力",
            f"{pressure:.1f} bar"
        )

        st.metric(
            "功率",
            f"{power:.1f} kW"
        )

        if status == "正常":
            st.success("🟢 当前状态：正常")
        elif status == "注意":
            st.warning("🟡 当前状态：需要关注")
        elif status == "警告":
            st.warning("🟠 当前状态：警告")
        else:
            st.error("🔴 当前状态：严重异常")

    st.divider()

    history = pd.read_csv(
        "pump_history.csv",
        encoding="utf-8-sig"
    )

    history["运行时间"] = (
        history["天数"].astype(str)
        + "-"
        + history["小时"].astype(str)
    )

    st.subheader("30天振动趋势")

    vibration_chart = history[
        ["运行时间", "振动"]
    ].copy()

    vibration_chart = vibration_chart.set_index(
        "运行时间"
    )

    st.line_chart(
        vibration_chart,
        y="振动"
    )


# ==========================================
# AI诊断
# ==========================================

elif menu == "AI诊断":

    st.title("AI智能诊断")

    st.caption(
        f"设备：{device_id}"
    )

    st.divider()

    st.subheader("当前设备状态")

    if status == "正常":

        st.success(
            "🟢 当前状态：正常"
        )

    elif status == "注意":

        st.warning(
            "🟡 当前状态：需要关注"
        )

    elif status == "警告":

        st.warning(
            "🟠 当前状态：警告"
        )

    else:

        st.error(
            "🔴 当前状态：严重异常"
        )

    st.subheader("当前运行参数")

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "振动",
            f"{vibration:.1f} mm/s"
        )

    with col2:

        st.metric(
            "温度",
            f"{temperature:.1f} °C"
        )

    with col3:

        st.metric(
            "功率",
            f"{power:.1f} kW"
        )

    st.divider()

    st.subheader("AI诊断结论")

    if status == "正常":

        st.success(
            "🟢 当前没有发现明显异常。"
        )

        st.write(
            "当前振动、温度和功率处于当前模拟规则的正常范围。"
        )

        st.info(
            "建议：继续监测设备运行状态。"
        )

    elif status == "注意":

        st.warning(
            "🟡 设备参数出现变化，需要加强监测。"
        )

    elif status == "警告":

        st.warning(
            "🟠 发现设备异常趋势。"
        )

        st.write(
            "建议重点检查轴承、润滑和联轴器。"
        )

    else:

        st.error(
            "🔴 发现严重异常。"
        )

        st.write(
            "建议检查轴承、润滑和联轴器，"
            "并根据现场安全规程决定后续处置。"
        )

    st.divider()

    st.subheader("最近一次维修")

    if latest_repair is not None:

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "工单编号",
                str(latest_repair["工单编号"])
            )

        with col2:

            st.metric(
                "维修状态",
                str(latest_repair["状态"])
            )

        with col3:

            st.metric(
                "维修班组",
                str(latest_repair["维修班组"])
            )

        st.write(
            f"维修结果：{latest_repair['维修结果']}"
        )

        st.write(
            f"处理措施：{latest_repair['处理措施']}"
        )

    else:

        st.info(
            "暂时没有维修记录。"
        )

    st.divider()

    st.subheader("维修效果")

    if vibration_improvement is not None:

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "振动下降",
                f"{vibration_improvement:.1f}%"
            )

        with col2:

            st.metric(
                "功率下降",
                f"{power_saving:.1f} kW"
            )

        st.write(
            f"维修前振动：{before_vibration:.1f} mm/s"
        )

        st.write(
            f"维修后振动：{after_vibration:.1f} mm/s"
        )

        st.write(
            f"维修前功率：{before_power:.1f} kW"
        )

        st.write(
            f"维修后功率：{after_power:.1f} kW"
        )

        if after_vibration < before_vibration:

            st.success(
                f"✅ 当前模拟数据显示维修有效，"
                f"振动下降 {vibration_improvement:.1f}%。"
            )

    else:

        st.info(
            "暂无维修效果数据。"
        )

    st.divider()

    st.subheader("AI Agent")

    st.write(
        "点击按钮，让网页直接调用工业泵 AI Agent。"
    )

    if st.button(
        "运行 AI Agent",
        type="primary"
    ):

        with st.spinner(
            "AI Agent 正在分析设备..."
        ):

            result = subprocess.run(
                [
                    sys.executable,
                    "industrial_agent.py"
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace"
            )

        if result.returncode == 0:

            st.success(
                "✅ AI Agent 运行完成"
            )

            output = result.stdout

            if "当前AI状态：正常" in output:

                st.success(
                    "🟢 AI Agent最终判断：设备正常"
                )

            elif "当前AI状态：严重异常" in output:

                st.error(
                    "🔴 AI Agent最终判断：严重异常"
                )

            elif "当前AI状态：警告" in output:

                st.warning(
                    "🟠 AI Agent最终判断：警告"
                )

            if "维修状态：维修后状态改善" in output:

                st.success(
                    "✅ 维修状态：维修后状态改善"
                )

            elif "维修状态：等待维修" in output:

                st.warning(
                    "⚠️ 维修状态：等待维修"
                )

            with st.expander(
                "查看 AI Agent 详细运行日志"
            ):

                st.code(
                    output,
                    language="text"
                )

        else:

            st.error(
                "❌ AI Agent 运行失败"
            )

            with st.expander(
                "查看错误信息"
            ):

                st.code(
                    result.stderr,
                    language="text"
                )


# ==========================================
# 维修工单
# ==========================================

elif menu == "维修工单":

    st.title("维修工单管理")

    st.caption(
        f"设备：{device_id}"
    )

    st.divider()

    try:

        tasks = pd.read_csv(
            "maintenance_tasks.csv",
            encoding="utf-8-sig"
        )

        results = pd.read_csv(
            "maintenance_results.csv",
            encoding="utf-8-sig"
        )

        device_tasks = tasks[
            tasks["设备编号"] == device_id
        ]

        if len(device_tasks) > 0:

            task = device_tasks.iloc[-1]

            task_id = str(task["工单编号"])

            st.subheader("当前维修工单")

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "工单编号",
                    task_id
                )

            with col2:

                st.metric(
                    "优先级",
                    str(task["优先级"])
                )

            with col3:

                st.metric(
                    "工单状态",
                    str(task["状态"])
                )

            st.write(
                f"**问题：** {task['问题']}"
            )

            st.write(
                f"**建议检查：** {task['建议检查']}"
            )

            st.divider()

            st.subheader("维修反馈")

            matched = results[
                results["工单编号"] == task["工单编号"]
            ]

            if len(matched) > 0:

                repair = matched.iloc[-1]

                st.success(
                    "维修反馈已找到"
                )

                st.write(
                    f"**维修结果：** {repair['维修结果']}"
                )

                st.write(
                    f"**处理措施：** {repair['处理措施']}"
                )

                st.write(
                    f"**维修人员：** {repair['维修人员']}"
                )

                st.write(
                    f"**维修班组：** {repair['维修班组']}"
                )

                st.write(
                    f"**状态：** {repair['状态']}"
                )

            else:

                st.warning(
                    "暂时没有找到该工单的维修反馈。"
                )

        else:

            st.info(
                "当前设备没有维修工单。"
            )

    except Exception as e:

        st.error(
            f"读取维修工单失败：{e}"
        )


# ==========================================
# 能耗分析
# ==========================================

elif menu == "能耗分析":

    st.title("设备能耗分析")

    st.caption(
        f"设备：{device_id}"
    )

    st.divider()

    if (
        before_power is not None
        and after_power is not None
    ):

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "维修前功率",
                f"{before_power:.1f} kW"
            )

        with col2:

            st.metric(
                "维修后功率",
                f"{after_power:.1f} kW"
            )

        with col3:

            st.metric(
                "功率下降",
                f"{power_saving:.1f} kW",
                f"{power_saving_percent:.1f}%"
            )

        st.divider()

        st.subheader("AI能耗分析")

        if power_saving > 0:

            st.success(
                f"当前模拟数据中，维修后功率下降 "
                f"{power_saving:.1f} kW，"
                f"下降比例 {power_saving_percent:.1f}%。"
            )

            st.info(
                "注意：这里是模拟维修前后数据，"
                "不能直接作为真实节电量或节约电费的结论。"
            )

        elif power_saving == 0:

            st.warning(
                "维修前后功率没有变化。"
            )

        else:

            st.warning(
                "维修后功率上升，建议进一步检查运行工况。"
            )

    else:

        st.info(
            "暂无维修前后能耗数据。"
        )
