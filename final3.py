import streamlit as st
import plotly.graph_objects as go

# -----------------------------
# ฟังก์ชันคำนวณ
# -----------------------------
def calculate_volume(w, l, h):
    return w * l * h

def sort_boxes_by_volume(boxes):
    return sorted(boxes, key=lambda b: calculate_volume(b['width'], b['length'], b['height']), reverse=True)

def pack_boxes(container_dim, max_weight, boxes):
    w, l, h = container_dim
    used_volume = 0
    total_weight = 0
    packed_boxes = []
    pos_x = pos_y = pos_z = 0
    current_layer_height = 0

    for box in sort_boxes_by_volume(boxes):
        for _ in range(box['quantity']):
            if (pos_x + box['width'] <= w and
                pos_y + box['length'] <= l and
                pos_z + box['height'] <= h):

                if total_weight + box['weight'] > max_weight:
                    break

                packed_boxes.append({
                    'id': box['id'],
                    'pos': (pos_x, pos_y, pos_z),
                    'dim': (box['width'], box['length'], box['height']),
                    'weight': box['weight']
                })

                used_volume += calculate_volume(box['width'], box['length'], box['height'])
                total_weight += box['weight']
                pos_x += box['width']

                if pos_x >= w:
                    pos_x = 0
                    pos_y += box['length']
                    if pos_y >= l:
                        pos_y = 0
                        pos_z += current_layer_height
                        current_layer_height = 0

                current_layer_height = max(current_layer_height, box['height'])
            else:
                break

    container_volume = calculate_volume(w, l, h)
    used_percent = (used_volume / container_volume) * 100
    return packed_boxes, used_percent, total_weight

def visualize_boxes(packed_boxes):
    fig = go.Figure()
    for box in packed_boxes:
        x, y, z = box['pos']
        w, l, h = box['dim']

        fig.add_trace(go.Mesh3d(
            x=[x, x+w, x+w, x, x, x+w, x+w, x],
            y=[y, y, y+l, y+l, y, y, y+l, y+l],
            z=[z, z, z, z, z+h, z+h, z+h, z+h],
            color='lightblue',
            opacity=0.5,
            alphahull=0,
            name=f"Box {box['id']}"
        ))

    fig.update_layout(
        scene=dict(
            xaxis_title='Width (cm)',
            yaxis_title='Length (cm)',
            zaxis_title='Height (cm)'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        title="📦 ภาพจำลองการจัดเรียงกล่องในตู้คอนเทนเนอร์"
    )
    st.plotly_chart(fig)

# -----------------------------
# UI เริ่มต้น
# -----------------------------
st.title("🚢 Container Packing Planner")
st.markdown("ระบบจำลองการจัดเรียงกล่องสินค้าใน **ตู้คอนเทนเนอร์** แบบ 3 มิติ")

# 🔲 ตัวเลือกตู้คอนเทนเนอร์
container_options = {
    "ตู้ 20 ฟุต (20ft)": {
        "width": 244, "length": 610, "height": 251, "empty_weight": 2200
    },
    "ตู้ 40 ฟุต (40ft)": {
        "width": 244, "length": 1219, "height": 251, "empty_weight": 3800
    },
    "ตู้ 40 ฟุต High Cube": {
        "width": 244, "length": 1219, "height": 290, "empty_weight": 3900
    },
    "ตู้ 45 ฟุต (45ft)": {
        "width": 244, "length": 1370, "height": 290, "empty_weight": 4000
    }
}

selected_container = st.selectbox("เลือกขนาดตู้คอนเทนเนอร์", list(container_options.keys()))
container = container_options[selected_container]

# น้ำหนักบรรทุกสูงสุดสมมุติ (รวมตู้)
max_total_weight = 30000  # กิโลกรัม
available_weight = max_total_weight - container['empty_weight']

st.info(f"""
📏 **ขนาดตู้:**  
- กว้าง: {container['width']} cm  
- ยาว: {container['length']} cm  
- สูง: {container['height']} cm  
⚖️ **น้ำหนักบรรทุกสุทธิได้:** {available_weight} กก. (หลังหักน้ำหนักตู้)
""")

# 📦 กล่องตัวอย่าง
boxes = [
    {'id': 'A', 'width': 50, 'length': 60, 'height': 40, 'weight': 30, 'quantity': 4},
    {'id': 'B', 'width': 40, 'length': 40, 'height': 40, 'weight': 20, 'quantity': 10},
    {'id': 'C', 'width': 100, 'length': 100, 'height': 50, 'weight': 80, 'quantity': 1},
]

if st.button("🚀 คำนวณการจัดวางกล่อง"):
    dim = (container['width'], container['length'], container['height'])
    packed_boxes, used_percent, total_weight = pack_boxes(dim, available_weight, boxes)

    st.subheader("📊 สรุปผล")
    st.write(f"✅ พื้นที่ใช้งาน: **{used_percent:.2f}%**")
    st.write(f"⚖️ น้ำหนักรวมกล่อง: **{total_weight:.2f} กก.** / {available_weight:.0f} กก.")

    if total_weight >= available_weight:
        st.warning("⚠️ น้ำหนักเกินขีดจำกัดของตู้ กรุณาลดจำนวนหรือขนาดกล่อง")

    visualize_boxes(packed_boxes)
else:
    st.info("กรุณากดปุ่มด้านบนเพื่อเริ่มการคำนวณจัดเรียงกล่อง")
