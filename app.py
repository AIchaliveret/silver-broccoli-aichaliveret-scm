import streamlit as st
import pandas as pd

st.set_page_config(page_title="AICHALIVERET - KLIK PIHAK SAAS SCM", page_icon="👔", layout="wide")

YARD_TO_METER = 0.9144
def yard_to_meter(y): return y * YARD_TO_METER
def calc_kodi(m, cm):
    pcs = m/(cm/100) if cm else 0
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
jml = st.sidebar.number_input("Jumlah Ball", 1, 20, len(st.session_state.balls))
roll = st.sidebar.slider("Roll per Ball", 10, 12, 11)
pot = st.sidebar.multiselect("Potongan cm", [100,120,180,240,270,300,340], default=[180])

if jml!= len(st.session_state.balls):
    if jml > len(st.session_state.balls):
        for i in range(len(st.session_state.balls), jml):
            st.session_state.balls.append({"no_serie": f"BS-00{i+1}A", "yard": 1200})
    else:
        st.session_state.balls = st.session_state.balls[:jml]

total_yard = sum(b["yard"] for b in st.session_state.balls)
total_meter = yard_to_meter(total_yard)
total_roll = len(st.session_state.balls)*roll

st.title("Team AICHALIVERET — KLIK PIHAK SAAS SCM")
st.caption("Direktur → Manufaktur → CMT → Pooling → Supir GPS | Yard→Meter→Kodi")

c1,c2,c3,c4 = st.columns(4)
c1.metric("Total Ball", f"{len(st.session_state.balls)} Ball", f"{total_yard} Yard")
c2.metric("Total Meter", f"{total_meter:,.1f} m")
c3.metric("Total Roll", f"{total_roll} Roll")
main = pot[0] if pot else 180
k,_ = calc_kodi(yard_to_meter(total_yard/total_roll) if total_roll else 0, main)
c4.metric("Total Kodi", f"{k*total_roll:.1f} Kodi", f"@{main}cm")

left,mid,right = st.columns(3)
with left:
    st.markdown("**COLUMN 1: TERIMA PO/SJ**")
    for i,b in enumerate(st.session_state.balls):
        with st.container(border=True):
            serie = st.text_input(f"Serie {i}", b["no_serie"], key=f"s{i}")
            yard = st.number_input(f"Yard {i}", value=b["yard"], key=f"y{i}")
            st.session_state.balls[i] = {"no_serie": serie, "yard": yard}
            st.caption(f"{yard} Yard = {yard_to_meter(yard):.2f}m")

with mid:
    st.markdown("**COLUMN 2: MANUFACTURE WIP**")
    for r in range(min(total_roll, 12)):
        idx = r // roll
        by = st.session_state.balls[idx]["yard"] if idx < len(st.session_state.balls) else 0
        rm = yard_to_meter(by/roll if roll else 0)
        kd,_ = calc_kodi(rm, main)
        with st.container(border=True):
            st.text(f"{st.session_state.balls[idx]['no_serie']}-R{r%roll+1}")
            st.caption(f"{rm:.2f}m = {kd:.2f} Kodi")

with right:
    st.markdown("**COLUMN 3: WIP → KIRIM + GPS**")
    total_pakai = 0
    for i in range(min(5, len(st.session_state.balls))):
        pakai = st.number_input(f"Ball {i+1} pakai Kodi", 0.0, 20.0, 4.0, key=f"p{i}")
        total_pakai += pakai
    st.text_input("Supir", "Budi TRK-01")
    st.text_input("No Polisi", "B 1234 CD")
    alamat = st.text_input("Alamat Via titik", "Cimahi -6.8731,107.5423")
    st.link_button("📍 Buka GPS Maps", f"https://maps.google.com/?q={alamat.split(',')[-1]}")
    st.checkbox("Sampai tujuan - foto")
