import streamlit as st
import plotly.graph_objects as go

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
        title="📦 ภาพจำลองการจัดเรียงกล่อง"
    )
    st.plotly_chart(fig)

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("📦 Vehicle Space Utilization Planner")
st.markdown("ระบบจำลองการวางกล่องในรถขนส่ง หรือ ตู้คอนเทนเนอร์")

mode = st.radio("เลือกประเภทการจำลอง", ["รถขนส่ง", "ตู้คอนเทนเนอร์"])

# กล่องสินค้า (ตัวอย่าง)
boxes = [
    {'id': 'A', 'width': 50, 'length': 60, 'height': 40, 'weight': 30, 'quantity': 4},
    {'id': 'B', 'width': 40, 'length': 40, 'height': 40, 'weight': 20, 'quantity': 10},
    {'id': 'C', 'width': 100, 'length': 100, 'height': 50, 'weight': 80, 'quantity': 1},
]

if mode == "รถขนส่ง":
    truck_types = {
        "รถบรรทุก 4 ล้อ": 9.5,
        "รถบรรทุก 6 ล้อ": 15,
        "รถบรรทุก 10 ล้อ": 25,
        "รถบรรทุก 12 ล้อ": 30,
        "รถพ่วง 18 ล้อ": 47,
        "รถพ่วง 22 ล้อ/24 ล้อ": 50.5
    }

    selected_truck = st.selectbox("🚚 เลือกประเภทรถบรรทุก", list(truck_types.keys()))
    max_weight_kg = truck_types[selected_truck] * 1000

    st.subheader("📐 ขนาดของรถบรรทุก (กำหนดเอง)")
    truck_w = st.number_input("ความกว้างรถ (cm)", min_value=50, max_value=500, value=200)
    truck_l = st.number_input("ความยาวรถ (cm)", min_value=50, max_value=2000, value=400)
    truck_h = st.number_input("ความสูงรถ (cm)", min_value=50, max_value=500, value=180)

    if st.button("🔍 คำนวณการจัดวาง (รถบรรทุก)"):
        truck_dim = (truck_w, truck_l, truck_h)
        packed_boxes, used_percent, total_weight = pack_boxes(truck_dim, max_weight_kg, boxes)

        st.subheader("📊 สรุปผลการจัดวาง")
        st.write(f"- พื้นที่ที่ใช้: **{used_percent:.2f}%**")
        st.write(f"- น้ำหนักรวมกล่อง: **{total_weight:.2f} กก.** / จำกัด {max_weight_kg:.0f} กก.")
        visualize_boxes(packed_boxes)

elif mode == "ตู้คอนเทนเนอร์":
    containers = {
        "ตู้คอนเทนเนอร์ 20 ฟุต": {"width": 244, "length": 610, "height": 251, "weight": 2200},
        "ตู้คอนเทนเนอร์ 40 ฟุต": {"width": 244, "length": 1219, "height": 251, "weight": 3800},
        "ตู้คอนเทนเนอร์ 40 ฟุต High Cube": {"width": 244, "length": 1219, "height": 290, "weight": 3900},
        "ตู้คอนเทนเนอร์ 45 ฟุต": {"width": 244, "length": 1370, "height": 290, "weight": 4100},
        "ตู้คอนเทนเนอร์พื้นเรียบ 40 ฟุต": {"width": 244, "length": 1219, "height": 251, "weight": 40000}
    }

    selected_container = st.selectbox("🚢 เลือกตู้คอนเทนเนอร์", list(containers.keys()))
    container = containers[selected_container]
    max_weight = container["weight"] + 30000  # น้ำหนักสูงสุดรวมสินค้า (ประมาณ)

    st.write(f"**ขนาด:** กว้าง {container['width']} cm, ยาว {container['length']} cm, สูง {container['height']} cm")
    st.write(f"**น้ำหนักเปล่า:** {container['weight']} กก.")

    if st.button("🔍 คำนวณการจัดวาง (ตู้คอนเทนเนอร์)"):
        truck_dim = (container['width'], container['length'], container['height'])
        packed_boxes, used_percent, total_weight = pack_boxes(truck_dim, max_weight, boxes)

        st.subheader("📊 สรุปผลการจัดวาง")
        st.write(f"- พื้นที่ที่ใช้: **{used_percent:.2f}%**")
        st.write(f"- น้ำหนักรวมกล่อง: **{total_weight:.2f} กก.**")
        visualize_boxes(packed_boxes)
