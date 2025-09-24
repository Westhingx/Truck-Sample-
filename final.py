import streamlit as st
import plotly.graph_objects as go

# ขนาดรถบรรทุก
truck_dimensions = (200, 400, 180)

# รายการกล่องสินค้า
boxes = [
    {'id': 'A', 'width': 50, 'length': 60, 'height': 40, 'quantity': 4},
    {'id': 'B', 'width': 40, 'length': 40, 'height': 40, 'quantity': 10},
    {'id': 'C', 'width': 100, 'length': 100, 'height': 50, 'quantity': 1},
]

# ฟังก์ชันจัดเรียงกล่อง
def calculate_volume(w, l, h):
    return w * l * h

def sort_boxes_by_volume(boxes):
    return sorted(boxes, key=lambda b: calculate_volume(b['width'], b['length'], b['height']), reverse=True)

def pack_boxes(truck_dimensions, boxes):
    truck_w, truck_l, truck_h = truck_dimensions
    used_space = 0
    packed_boxes = []
    position_x, position_y, position_z = 0, 0, 0
    current_layer_height = 0

    for box in sort_boxes_by_volume(boxes):
        for _ in range(box['quantity']):
            if (position_x + box['width'] <= truck_w and
                position_y + box['length'] <= truck_l and
                position_z + box['height'] <= truck_h):

                packed_boxes.append({
                    'id': box['id'],
                    'pos': (position_x, position_y, position_z),
                    'dim': (box['width'], box['length'], box['height'])
                })

                used_space += calculate_volume(box['width'], box['length'], box['height'])

                position_x += box['width']
                if position_x >= truck_w:
                    position_x = 0
                    position_y += box['length']
                    if position_y >= truck_l:
                        position_y = 0
                        position_z += current_layer_height
                        current_layer_height = 0

                current_layer_height = max(current_layer_height, box['height'])
            else:
                break

    truck_volume = calculate_volume(truck_w, truck_l, truck_h)
    used_percent = (used_space / truck_volume) * 100

    return packed_boxes, used_percent

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
            name=box['id']
        ))

    fig.update_layout(
        scene=dict(
            xaxis_title='Width',
            yaxis_title='Length',
            zaxis_title='Height'
        ),
        margin=dict(l=0, r=0, b=0, t=0)
    )
    st.plotly_chart(fig)

# รันแอป
st.title("📦

