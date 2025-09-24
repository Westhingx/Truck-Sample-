import streamlit as st
import plotly.graph_objects as go

# ฟังก์ชันคำนวณปริมาตรกล่อง
def calculate_volume(w, l, h):
    return w * l * h

# ฟังก์ชันเรียงกล่องจากใหญ่ไปเล็ก (ตามปริมาตร)
def sort_boxes_by_volume(boxes):
    return sorted(boxes, key=lambda b: calculate_volume(b['width'], b['length'], b['height']), reverse=True)

# ฟังก์ชันจัดวางกล่องแบบง่ายในรถ 3D
def pack_boxes(truck_dimensions, boxes):
    truck_w, truck_l, truck_h = truck_dimensions
    used_volume = 0
    packed_boxes = []
    pos_x, pos_y, pos_z = 0, 0, 0
    current_layer_height = 0

    for box in sort_boxes_by_volume(boxes):
        for _ in range(box['quantity']):
            # ตรวจสอบว่ากล่องนี้วางได้ไหมในตำแหน่งปัจจุบัน
            if (pos_x + box['width'] <= truck_w and
                pos_y + box['length'] <= truck_l and
                pos_z + box['height'] <= truck_h):

                packed_boxes.append({
                    'id': box['id'],
                    'pos': (pos_x, pos_y, pos_z),
                    'dim': (box['width'], box['length'], box['height'])
                })

                used_volume += calculate_volume(box['width'], box['length'], box['height'])

                pos_x += box['width']  # วางกล่องถัดไปทางแกน x

                # ถ้าเต็มแกน x ให้เลื่อนไปแกน y
                if pos_x >= truck_w:
                    pos_x = 0
                    pos_y += box['length']

                    # ถ้าเต็มแกน y ให้เลื่อนขึ้นแกน z (ชั้นใหม่)
                    if pos_y >= truck_l:
                        pos_y = 0
                        pos_z += current_layer_height
                        current_layer_height = 0

                # อัพเดทความสูงสูงสุดของชั้นนี้
                current_layer_height = max(current_layer_height, box['height'])
            else:
                # ถ้าวางไม่ได้แล้ว หยุดวางกล่องนี้
                break

    truck_volume = calculate_volume(truck_w, truck_l, truck_h)
    used_percent = (used_volume / truck_volume) * 100

    return packed_boxes, used_percent

# ฟังก์ชันแสดงภาพ 3D ของกล่องที่วาง
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
            zaxis_title='สูง (cm)',
            xaxis=dict(nticks=5, range=[0, 250]),
            yaxis=dict(nticks=5, range=[0, 500]),
            zaxis=dict(nticks=5, range=[0, 200]),
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        title="ภาพจำลองการจัดเรียงกล่องในรถบรรทุก"
    )

    st.plotly_chart(fig)

# --- เริ่มเขียนส่วน Streamlit UI ---

st.title("📦 Vehicle Space Utilization Planner (ระบบจัดการพื้นที่บนรถขนส่ง)")

st.markdown("""
ระบบนี้จะช่วยจัดเรียงกล่องสินค้าบนรถบรรทุก เพื่อใช้พื้นที่ให้เกิดประโยชน์สูงสุด  
กรุณากรอกขนาดของรถและกดปุ่มคำนวณ เพื่อดูภาพจำลองและสรุปพื้นที่ที่ใช้งาน
""")

# ป้อนขนาดรถ (หน่วยเป็นเซนติเมตร)
truck_width = st.number_input("ความกว้างรถ (cm)", min_value=50, max_value=500, value=200)
truck_length = st.number_input("ความยาวรถ (cm)", min_value=50, max_value=1000, value=400)
truck_height = st.number_input("ความสูงรถ (cm)", min_value=50, max_value=500, value=180)

# รายการกล่องตัวอย่าง (แก้ไขได้ในโค้ด)
boxes = [
    {'id': 'A', 'width': 50, 'length': 60, 'height': 40, 'quantity': 4},
    {'id': 'B', 'width': 40, 'length': 40, 'height': 40, 'quantity': 10},
    {'id': 'C', 'width': 100, 'length': 100, 'height': 50, 'quantity': 1},
]

if st.button("คำนวณการจัดวางกล่อง"):
    truck_dim = (truck_width, truck_length, truck_height)

    # เรียกฟังก์ชันจัดกล่อง
    packed_boxes, used_percent = pack_boxes(truck_dim, boxes)

    st.write(f"ใช้พื้นที่ไปแล้ว: **{used_percent:.2f}%** จากทั้งหมด")

    # แสดงภาพ 3D
    visualize_boxes(packed_boxes)

else:
    st.write("กรุณากดปุ่ม ‘คำนวณการจัดวางกล่อง’ เพื่อเริ่มการจำลอง")
