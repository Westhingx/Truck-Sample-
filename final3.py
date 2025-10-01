import streamlit as st 
import plotly.graph_objects as go

# -----------------------------
# ฟังก์ชันการคำนวณต่าง ๆ
# -----------------------------
def calculate_volume(w, l, h):
    return w * l * h

def sort_boxes_by_volume(boxes):
    return sorted(boxes, key=lambda b: calculate_volume(b['width'], b['length'], b['height']), reverse=True)

def pack_boxes(truck_dimensions, max_weight, boxes):
    truck_w, truck_l, truck_h = truck_dimensions
    used_volume = 0
    total_weight = 0
    packed_boxes = []
    pos_x, pos_y, pos_z = 0, 0, 0
    current_layer_height = 0

    for box in sort_boxes_by_volume(boxes):
        for _ in range(box['quantity']):
            if (pos_x + box['width'] <= truck_w and
                pos_y + box['length'] <= truck_l and
                pos_z + box['height'] <= truck_h):
                
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

                if pos_x >= truck_w:
                    pos_x = 0
                    pos_y += box['length']
                    if pos_y >= truck_l:
                        pos_y = 0
                        pos_z += current_layer_height
                        current_layer_height = 0

                current_layer_height = max(current_layer_height, box['height'])
            else:
                break

    truck_volume = calculate_volume(truck_w, truck_l, truck_h)
    used_percent = (used_volume / truck_volume) * 100

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
# เริ่มต้นส่วนของ Streamlit UI
# -----------------------------
st.title("📦 Vehicle Space Utilization Planner")

st.markdown("""
ระบบช่วยจำลองการจัดกล่องสินค้าในตู้คอนเทนเนอร์  
**พร้อมคำนึงถึงน้ำหนักและขนาดตู้ที่เลือก**
""")

# ✅ ตัวเลือกตู้คอนเทนเนอร์
container_types = {
    "ตู้คอนเทนเนอร์ 20 ฟุต": {
        "width": 244, "length": 610, "height": 251, "empty_weight": 2200
    },
    "ตู้คอนเทนเนอร์ 40 ฟุต": {
        "width": 244, "length": 1219, "height": 251, "empty_weight": 3800
    },
    "ตู้คอนเทนเนอร์ 40 ฟุต High Cube": {
        "width": 244, "length": 1219, "height": 290, "empty_weight": 3900
    },
    "ตู้คอนเทนเนอร์ 45 ฟุต": {
        "width": 244, "length": 1370, "height": 290, "empty_weight": 4000
    }
}

selected_container = st.selectbox("🚢 เลือกขนาดตู้คอนเทนเนอร์", list(container_types.keys()))
container = container_types[selected_container]

st.success(f"""
**ขนาดตู้:** {selected_container}  
- กว้าง: {container['width']} cm  
- ยาว: {container['length']} cm  
- สูง: {container['height']} cm  
- น้ำหนักเปล่า: {container['empty_weight']} กก.
""")

# ใส่น้ำหนักรวมที่อนุญาต (เช่น 30,000 kg ลบด้วยน้ำหนักเปล่า)
max_total_weight = 30000  # น้ำหนักรวมสูงสุดของตู้
max_weight_kg = max_total_weight - container["empty_weight"]

# 📦 รายการกล่องสินค้า (ตัวอย่าง fix)
boxes = [
    {'id': 'A', 'width': 50, 'length': 60, 'height': 40, 'weight': 30, 'quantity': 4},
    {'id': 'B', 'width': 40, 'length': 40, 'height': 40, 'weight': 20, 'quantity': 10},
    {'id': 'C', 'width': 100, 'length': 100, 'height': 50, 'weight': 80, 'quantity': 1},
]

# 🧮 ปุ่มคำนวณ
if st.button("🔍 คำนวณการจัดวางกล่อง"):
    truck_dim = (container["width"], container["length"], container["height"])
    packed_boxes, used_percent, total_weight = pack_boxes(truck_dim, max_weight_kg, boxes)

    st.subheader("📊 สรุปผลการจัดวาง")
    st.write(f"- พื้นที่ที่ใช้: **{used_percent:.2f}%** ของพื้นที่ทั้งหมด")
    st.write(f"- น้ำหนักรวมของกล่อง: **{total_weight:.2f} กก.** / จำกัดสูงสุด {max_weight_kg:.0f} กก.")

    if total_weight >= max_weight_kg:
        st.warning("⚠️ น้ำหนักรวมเกินขีดจำกัด กรุณาปรับจำนวนหรือขนาดกล่อง")

    visualize_boxes(packed_boxes)

else:
    st.info("กดปุ่มด้านบนเพื่อเริ่มคำนวณการจัดวางกล่อง")
