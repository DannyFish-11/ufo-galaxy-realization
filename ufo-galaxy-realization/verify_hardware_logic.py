import sys
import os
import asyncio
import logging
from datetime import datetime

# 添加路径以导入模块
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 模拟 EventBus
class MockEventBus:
    def __init__(self):
        self.events = []

    def publish_sync(self, event_type, source, data):
        print(f"[EventBus] Event: {event_type}, Source: {source}, Data: {data}")
        self.events.append({
            "type": event_type,
            "source": source,
            "data": data
        })

# 替换真实的 EventBus
import system_integration.state_machine_ui_integration as sm_module
sm_module.event_bus = MockEventBus()

from system_integration.state_machine_ui_integration import SystemStateMachine, TriggerType, SystemState, EventType

async def test_hardware_wakeup_flow():
    print("=== 开始深度逻辑核查: 硬件唤醒 -> 文本聚焦 ===")
    
    # 1. 初始化状态机
    sm = SystemStateMachine()
    print(f"初始状态: {sm.current_state}")
    assert sm.current_state == SystemState.SLEEPING, "初始状态应为 SLEEPING"

    # 2. 模拟硬件触发 (快捷键)
    print("\n>>> 模拟按下快捷键 (Ctrl+Shift+Space)...")
    success = sm.wakeup(trigger_type=TriggerType.HARDWARE_BUTTON, trigger_source="keyboard_listener")
    
    # 3. 验证状态转换
    print(f"唤醒结果: {success}")
    print(f"当前状态: {sm.current_state}")
    assert success is True, "唤醒操作应返回 True"
    assert sm.current_state == SystemState.ISLAND, "唤醒后状态应为 ISLAND"

    # 4. 验证事件信号 (关键步骤)
    events = sm_module.event_bus.events
    wakeup_signal = next((e for e in events if e["type"] == EventType.WAKEUP_SIGNAL), None)
    
    if wakeup_signal:
        print("\n[关键验证] 检查 WAKEUP_SIGNAL 数据包:")
        data = wakeup_signal["data"]
        print(f"  - focus_input: {data.get('focus_input')}")
        print(f"  - input_mode: {data.get('input_mode')}")
        
        if data.get("focus_input") is True and data.get("input_mode") == "text":
            print("\n✅ 验证通过: UI 已收到强制聚焦指令 (Text-First Mode Confirmed)")
        else:
            print("\n❌ 验证失败: 信号中缺少聚焦指令或模式错误")
            sys.exit(1)
    else:
        print("\n❌ 验证失败: 未检测到 WAKEUP_SIGNAL 事件")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(test_hardware_wakeup_flow())
