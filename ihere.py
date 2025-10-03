import streamlit as st
import plotly.graph_objects as go

# -------------------------
# ข้อมูลตู้คอนเทนเนอร์
# -------------------------
containers = {
    "ตู้คอนเทนเนอร์ 20 ฟุต": {
        "width": 244, "length": 610, "height": 251, "empty_weight": 2200
    },
    "ตู้คอนเทนเนอร์ 40 ฟุต": {
        "width": 244, "length": 1220, "height": 251, "empty_weight": 3800
    },
    "ตู้คอนเทนเนอร์ 40 ฟุต High Cube": {
        "width": 244, "length": 1220, "height": 290, "empty_weight": 3900
    }
}

# -------------------------
# ข้อมูลรถบรรทุก
# -------------------------
truck_types = {
    "รถบรรทุก 4 ล้อ": {"max_weight": 9500},
    "รถบรรทุก 6 ล้อ": {"max_weight": 15000},
    "รถบรรทุก 10 ล้อ": {"max_weight": 25000},
    "รถบรรทุก 12 ล้อ": {"max_weight": 30000}
}

# -------------------------
# ฟังก์ชันคำนวณ
# -------------------------
def calculate_volume(w, l, h):
    return w * l * h

def sort_boxes_by_volume(boxes):
    return sorted(boxes, key=lambda b: calculate_volume(b['width'], b['length'], b['height']), reverse=True)

def pack_boxes(space_w, space_l, space_h, max_weight, boxes):
    used_volume = 0
    total_weight = 0
    packed_boxes = []

    pos_x, pos_y, pos_z = 0, 0, 0
    current_layer_height = 0

    for box in sort_boxes_by_volume(boxes):
        for _ in range(box['quantity']):
            if (pos_x + box['width'] <= space_w and
                pos_y + box['length'] <= space_l and
                pos_z + box['height'] <= space_h):
                
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

                if pos_x >= space_w:
                    pos_x = 0
                    pos_y += box['length']
                    if pos_y >= space_l:
                        pos_y = 0
                        pos_z += current_layer_height
                        current_layer_height = 0

                current_layer_height = max(current_layer_height, box['height'])
            else:
                break

    total_volume = calculate_volume(space_w, space_l, space_h)
    used_percent = (used_volume / total_volume) * 100

    return packed_boxes, used_percent, total_weight

# -------------------------
# Visualize
# -------------------------
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
        title="📦 ภาพจำลองการจัดเรียงกล่อง"
    )
    st.plotly_chart(fig)

# -------------------------
# เริ่มต้น Streamlit
# -------------------------
st.title("📦 ระบบจำลองการวางกล่อง")
st.markdown("ระบบจำลองการวางกล่องใน **รถขนส่ง / ตู้คอนเทนเนอร์**")

# -------------------------
# เลือกประเภทการใช้งาน
# -------------------------
mode = st.radio("เลือกรูปแบบ:", ["🚛 รถบรรทุก", "🚢 ตู้คอนเทนเนอร์"])

if mode == "🚛 รถบรรทุก":
    truck_choice = st.selectbox("เลือกประเภทรถ:", list(truck_types.keys()))
    truck_data = truck_types[truck_choice]
    space_w = st.number_input("ความกว้างรถ (cm)", value=200)
    space_l = st.number_input("ความยาวรถ (cm)", value=500)
    space_h = st.number_input("ความสูงรถ (cm)", value=200)
    max_weight = truck_data["max_weight"]
    st.success(f"น้ำหนักบรรทุกสูงสุด: {max_weight} กก.")

else:
    container_choice = st.selectbox("เลือกตู้คอนเทนเนอร์:", list(containers.keys()))
    container = containers[container_choice]
    space_w = container["width"]
    space_l = container["length"]
    space_h = container["height"]
    max_weight = 28000  # ปกติตู้ขนส่งรับได้ ~28 ตัน
    st.info(f"""
    📦 ขนาด: {space_w} x {space_l} x {space_h} cm  
    ⚖️ น้ำหนักเปล่า: {container['empty_weight']} กก.  
    """)

# -------------------------
# รายการกล่องสินค้า
# -------------------------
st.subheader("📦 ข้อมูลกล่องสินค้า")

boxes = []
box_count = st.number_input("ระบุจำนวนกล่องที่ต้องการเพิ่ม", min_value=1, max_value=20, value=3)

for i in range(box_count):
    st.markdown(f"### กล่องที่ {i+1}")
    col1, col2, col3 = st.columns(3)
    with col1:
        width = st.number_input(f"กว้าง (cm) กล่อง {i+1}", key=f"w_{i}", min_value=1, value=40)
    with col2:
        length = st.number_input(f"ยาว (cm) กล่อง {i+1}", key=f"l_{i}", min_value=1, value=60)
    with col3:
        height = st.number_input(f"สูง (cm) กล่อง {i+1}", key=f"h_{i}", min_value=1, value=40)

    weight = st.number_input(f"น้ำหนัก (kg) กล่อง {i+1}", key=f"wt_{i}", min_value=1, value=10)
    qty = st.number_input(f"จำนวนกล่อง {i+1}", key=f"qty_{i}", min_value=1, value=1)

    boxes.append({
        "id": chr(65+i),
        "width": width,
        "length": length,
        "height": height,
        "weight": weight,
        "quantity": qty
    })

# -------------------------
# ปุ่มคำนวณ
# -------------------------
if st.button("🔍 คำนวณการจัดวางกล่อง"):
    packed_boxes, used_percent, total_weight = pack_boxes(space_w, space_l, space_h, max_weight, boxes)

    st.subheader("📊 สรุปผลการจัดวาง")
    st.write(f"🧱 พื้นที่ที่ใช้: **{used_percent:.2f}%**")
    st.write(f"⚖️ น้ำหนักรวมกล่อง: **{total_weight:.2f} กก.** / จำกัดสูงสุด {max_weight} กก.")

    if total_weight > max_weight:
        st.warning("⚠️ น้ำหนักรวมเกินขีดจำกัด กรุณาปรับขนาดหรือน้ำหนักกล่อง")

    visualize_boxes(packed_boxes)
