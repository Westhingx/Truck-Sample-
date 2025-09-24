import streamlit as st
import plotly.graph_objects as go

# ฟังก์ชันคำนวณปริมาตรกล่อง
def calculate_volume(w, l, h):
    return w * l * h

# เรียงกล่องตามปริมาตรจากมากไปน้อย
def sort_boxes_by_volume(boxes):
    return sorted(boxes, key=lambda b: calculate_volume(b['width'], b['length'], b['height']), reverse=True)

# ฟังก์ชันจัดวางกล่อง โดยคำนึงถึงน้ำหนักสูงสุดของรถ
def pack_boxes(truck_dimensions, max_weight, boxes):
    truck_w, truck_l, truck_h = truck_dimensions
    used_volume = 0
    total_weight = 0
    packed_boxes = []
    pos_x, pos_y, pos_z = 0, 0, 0
    current_layer_height = 0

    for box in sort_boxes_by_volume(boxes):
        for _ in range(box['quantity']):
            # ตรวจสอบว่าสามารถวางกล่องตามตำแหน่งได้ไหม
            if (pos_x + box['width'] <= truck_w and
                pos_y + box['length'] <= truck_l and
                pos_z + box['height'] <= truck_h):
                
                # ตรวจสอบน้ำหนักรวม ถ้าเกินหยุดวางกล่องนี้
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

# ฟังก์ชันแสดงภาพ 3D
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
            xaxis_title='กว้าง (cm)',
            yaxis_title='ยาว (cm)',
            zaxis_title='สูง (cm)'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        title="ภาพจำลองการจัดเรียงกล่องในรถบรรทุก"
    )
    st.plotly_chart(fig)

# --- UI Streamlit ---

st.title("📦 Vehicle Space Utilization Planner with Weight Limit")

st.markdown("""
เพิ่มฟีเจอร์น้ำหนักสินค้าและน้ำหนักสูงสุดที่รถรับได้ (กก.)  
กรุณากรอกข้อมูลด้านล่างและกดปุ่มคำนวณ
""")

# ขนาดรถ
truck_w = st.number_input("ความกว้างรถ (cm)", min_value=50, max_value=500, value=200)
truck_l = st.number_input("ความยาวรถ (cm)", min_value=50, max_value=1000, value=400)
truck_h = st.number_input("ความสูงรถ (cm)", min_value=50, max_value=500, value=180)

# น้ำหนักสูงสุดที่รถรับได้ (กก.)
max_weight = st.number_input("น้ำหนักสูงสุดที่รถรับได้ (กก.)", min_value=100, max_value=50000, value=5000)

# รายการกล่องสินค้า (แก้ไขน้ำหนักตามต้องการ)
boxes = [
    {'id': 'A', 'width': 50, 'length': 60, 'height': 40, 'weight': 30, 'quantity': 4},   # น้ำหนัก 30 kg/กล่อง
    {'id': 'B', 'width': 40, 'length': 40, 'height': 40, 'weight': 20, 'quantity': 10},  # น้ำหนัก 20 kg/กล่อง
    {'id': 'C', 'width': 100, 'length': 100, 'height': 50, 'weight': 80, 'quantity': 1}, # น้ำหนัก 80 kg/กล่อง
]

if st.button("คำนวณการจัดวางกล่อง"):
    truck_dim = (truck_w, truck_l, truck_h)
    packed_boxes, used_percent, total_weight = pack_boxes(truck_dim, max_weight, boxes)

    st.write(f"ใช้พื้นที่ไปแล้ว: **{used_percent:.2f}%** จากทั้งหมด")
    st.write(f"น้ำหนักรวมของกล่องที่จัดวาง: **{total_weight:.2f} กก.** จากน้ำหนักสูงสุดที่รับได้ {max_weight} กก.")

    if total_weight >= max_weight:
        st.warning("**น้ำหนักรวมเกินหรือเท่ากับน้ำหนักสูงสุดที่รถรับได้!** กรุณาปรับจำนวนกล่องหรือลดน้ำหนัก")

    visualize_boxes(packed_boxes)

else:
    st.write("กรุณากดปุ่ม ‘คำนวณการจัดวางกล่อง’ เพื่อเริ่มจำลอง")
