import streamlit as st
import pandas as pd

st.set_page_config(page_title="AICHALIVERET - KLIK PIHAK SaaS SCM", page_icon="👔", layout="wide")

YARD_TO_METER = 0.9144
def yard_to_meter(y): return y * YARD_TO_METER
def calc_kodi(meter, cm):
    pcs = meter / (cm/100) if cm else 0
    return pcs/20, pcs

if 'balls' not in st.session_state:
    st.session_state.balls = [
        {"no_serie": "BS-001A", "yard": 1207},
        {"no_serie": "BS-002B", "yard": 1254},
        {"no_serie": "BS-003C", "yard": 1304},
        {"no_serie": "BS-004D", "yard": 1180},
        {"no_serie": "BS-005E", "yard": 1220},
        {"no_serie": "BS-006F", "yard": 1280},
        {"no_serie": "BS-007G", "yard": 1284},
    ]

st.sidebar.title("Team AICHALIVERET")
st.sidebar.caption("KLIK PIHAK SAAS SCM\nTertib • Terkendali • Terpantau\nIBM BOB 2.0")
role = st.sidebar.radio("DIREKTUR KENDALIKAN SELURUH", ["DIREKTUR Full", "MANUFAKTUR", "CMT", "SUPIR"], 0)
jml_ball = st.sidebar.number_input("Jumlah Ball", 1, 20, len(st.session_state.balls))
roll_per_ball = st.sidebar.slider("Roll per Ball", 10, 12, 11)
potongan = st.sidebar.multiselect("Potongan cm", [100,120,180,240,270,300,340], default=[180])

# sync ball
if jml_ball!= len(st.session_state.balls):
    if jml_ball > len(st.session_state.balls):
        for i in range(len(st.session_state.balls), jml_ball):
            st.session_state.balls.append({"no_serie": f"BS-00{i+1}A", "yard": 1200})
    else:
        st.session_state.balls = st.session_state.balls[:jml_ball]

total_yard = sum(b["yard"] for b in st.session_state.balls)
total_meter = yard_to_meter(total_yard)
total_roll = len(st.session_state.balls) * roll_per_ball

st.title("Team AICHALIVERET — KLIK PIHAK SAAS SCM FOR GARMENT")
st.caption("Direktur → Manufaktur → CMT → Pooling → Supir GPS | Yard→Meter→Kodi")

if "DIREKTUR" in role:
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Total Ball", f"{len(st.session_state.balls)} Ball", f"{total_yard} Yard")
    c2.metric("Total Meter", f"{total_meter:,.1f} m")
    c3.metric("Total Roll", f"{total_roll} Roll")
    main_pot = potongan[0] if potongan else 180
    kodi,_ = calc_kodi(yard_to_meter(total_yard/total_roll) if total_roll else 0, main_pot)
    c4.metric("Total Kodi", f"{kodi*total_roll:.1f} Kodi", f"@{main_pot}cm")

st.divider()
left,mid,right = st.columns(3)

with left:
    st.markdown("**COLUMN 1: TERIMA PO/SJ**")
    st.caption(f"{len(st.session_state.balls)} Ball = {total_yard} Yard = {total_meter:.2f} Meter")
    for i,b in enumerate(st.session_state.balls):
        with st.container(border=True):
            serie = st.text_input(f"Serie {i}", b["no_serie"], key=f"s{i}")
            yard = st.number_input(f"Yard {i}", value=b["yard"], key=f"y{i}")
            st.session_state.balls[i] = {"no_serie": serie, "yard": yard}
            st.caption(f"{yard} Yard = {yard_to_meter(yard):.2f}m → auto Column2")

with mid:
    st.markdown("**COLUMN 2: MANUFACTURE WIP**")
    for r in range(min(total_roll, 12)):
        ball_idx = r // roll_per_ball
        byard = st.session_state.balls[ball_idx]["yard"] if ball_idx < len(st.session_state.balls) else 0
        r_yard = byard / roll_per_ball if roll_per_ball else 0
        r_meter = yard_to_meter(r_yard)
        kodi,_ = calc_kodi(r_meter, potongan[0] if potongan else 180)
        with st.container(border=True):
            st.text(f"{st.session_state.balls[ball_idx]['no_serie']}-R{r%roll_per_ball+1}")
            st.caption(f"{r_meter:.2f}m = {kodi:.2f} Kodi")

with right:
    st.markdown("**COLUMN 3: WIP TERPAKAI → KIRIM**")
    st.caption("Harus balance | GPS Maps Supir No Polisi Via titik")
    total_pakai = 0
    for i in range(min(5, len(st.session_state.balls))):
        pakai = st.number_input(f"Ball {i+1} pakai Kodi", 0.0, 20.0, 4.0, key=f"p{i}")
        total_pakai += pakai
    total_kodi_all = sum([calc_kodi(yard_to_meter(b["yard"]/roll_per_ball), potongan[0] if potongan else 180)[0]*roll_per_ball for b in st.session_state.balls])
    if abs(total_pakai - total_kodi_all) < 5:
        st.success(f"BALANCE {total_pakai:.1f} Kodi")
    else:
        st.error(f"SELISIH {total_kodi_all-total_pakai:.1f} Kodi")
    st.text_input("Supir", "Budi TRK-01")
    st.text_input("No Polisi", "B 1234 CD")
    alamat = st.text_input("Alamat Via titik", "Cimahi -6.8731,107.5423")
    st.link_button("Buka GPS Maps", f"https://maps.google.com/?q={alamat.split(',')[-1]}")
    st.checkbox("Sampai tujuan - foto")

st.sidebar.success("Main file path = app.py ✅")
