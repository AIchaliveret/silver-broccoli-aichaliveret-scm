import streamlit as st
import pandas as pd

st.set_page_config(page_title="AICHALIVERET SCM", page_icon="👔", layout="wide")
YARD_TO_METER = 0.9144
def ym(y): return y*0.9144
def kodi(m, cm): return (m/(cm/100)/20, m/(cm/100)) if cm else (0,0)

if 'balls' not in st.session_state:
    st.session_state.balls = [{"no_serie":"BS-001A","yard":1207},{"no_serie":"BS-002B","yard":1254},{"no_serie":"BS-003C","yard":1304}]
if 'rolls' not in st.session_state: st.session_state.rolls = []
if 'wip' not in st.session_state: st.session_state.wip = []
if 'supir' not in st.session_state: st.session_state.supir = {"nama":"","ktp":"","nopol":"","gps":"","sampai":False}

st.sidebar.title("Team AICHALIVERET")
st.sidebar.caption("KLIK PIHAK SAAS SCM\nTertib • Terkendali • Terpantau\nIBM BOB 2.0")
role = st.sidebar.radio("LOGIN SESUAI WEWENANG", ["DIREKTUR Full","MANUFAKTUR","CMT / Konveksi","SUPIR"], 0)

total_yard = sum(b["yard"] for b in st.session_state.balls)
total_m = ym(total_yard)

# === DIREKTUR - CUMA BOLEH INI ===
if role == "DIREKTUR Full":
    st.title("DIREKTUR — TERIMA PO/SJ")
    st.caption("Tugas: Input Jumlah Ball + Nomor Serie + Jumlah Yard (Google Form)")
    jml = st.number_input("Jumlah Ball",1,20,len(st.session_state.balls))
    if jml!=len(st.session_state.balls):
        if jml>len(st.session_state.balls):
            for i in range(len(st.session_state.balls),jml): st.session_state.balls.append({"no_serie":f"BS-00{i+1}A","yard":1200})
        else: st.session_state.balls = st.session_state.balls[:jml]
    if st.button("+ Tambah Ball"):
        st.session_state.balls.append({"no_serie":f"BS-00{len(st.session_state.balls)+1}A","yard":1200}); st.rerun()
    c1,c2 = st.columns(2); c1.metric("Jumlah Yard",f"{total_yard} Yard"); c2.metric("Meter",f"{total_m:.1f} m")
    for i,b in enumerate(st.session_state.balls):
        with st.container(border=True):
            col1,col2 = st.columns(2)
            with col1: b["no_serie"] = st.text_input(f"Ball {i+1} / Nomor Serie", b["no_serie"], key=f"d_s{i}")
            with col2: b["yard"] = st.number_input(f"Jumlah Yard", value=b["yard"], key=f"d_y{i}")
            st.caption(f"{b['yard']} Yard = {ym(b['yard']):.2f} m")
    if st.button("💾 SAVE → Kirim ke Manufacture",type="primary"): st.success("Terkirim ke Manufacture")

# === MANUFAKTUR - CUMA BOLEH INI ===
elif role == "MANUFAKTUR":
    st.title("MANUFAKTUR — Gudang / Potong")
    st.caption("Tugas: Pecah Ball jadi Roll, Potongan 180/240/270/300/340/Custom auto Kodi")
    if not st.session_state.balls: st.warning("Belum ada Ball dari Direktur"); st.stop()
    st.info(f"Terima: {len(st.session_state.balls)} Ball = {total_yard} Yard")
    # Auto jumlah Kodi sesuai coretan tangan lo
    c = st.columns(5)
    for idx, pot in enumerate([180,240,270,300,340]):
        c[idx].metric(f"Potongan {pot}cm =", f"{kodi(total_m,pot)[0]:.1f} Kodi")
    custom = st.number_input("Potongan Custom cm", 50,500,200)
    st.metric(f"Potongan Custom {custom}cm =", f"{kodi(total_m,custom)[0]:.1f}")
    st.divider()
    for b_idx,b in enumerate(st.session_state.balls):
        with st.expander(f"{b['no_serie']} - {b['yard']} Yard", expanded=True):
            existing = [r for r in st.session_state.rolls if r["ball_idx"]==b_idx]
            rc = st.number_input(f"Roll per Ball {b['no_serie']}",10,12,max(11,len(existing) or 11),key=f"m_rc{b_idx}")
            if len(existing)<rc:
                for r_i in range(len(existing),rc):
                    yp=b["yard"]/rc; st.session_state.rolls.append({"ball_idx":b_idx,"ball_serie":b["no_serie"],"roll_serie":f"{b['no_serie']}-R{r_i+1}","yard":int(yp),"potongan":180,"kodi":kodi(ym(yp),180)[0]})
                st.rerun()
            for r in [x for x in st.session_state.rolls if x["ball_idx"]==b_idx]:
                col1,col2,col3,col4 = st.columns(4)
                with col1: r["roll_serie"]=st.text_input("Roll / No Seri",r["roll_serie"],key=f"m_rs{b_idx}{r['roll_serie']}",label_visibility="collapsed")
                with col2: r["yard"]=st.number_input("Yard",value=r["yard"],key=f"m_y{b_idx}{r['roll_serie']}",label_visibility="collapsed")
                with col3: r["potongan"]=st.selectbox("Pot",[180,240,270,300,340,custom],key=f"m_p{b_idx}{r['roll_serie']}",label_visibility="collapsed")
                with col4:
                    m=ym(r["yard"]); kd,_=kodi(m,r["potongan"]); r["kodi"]=kd
                    st.caption(f"{m:.1f}m = {kd:.2f} Kodi @{r['potongan']}cm")
    if st.button("💾 SAVE → Kirim ke CMT",type="primary"): st.success("Terkirim ke CMT")

# === CMT ===
elif role == "CMT / Konveksi":
    st.title("CMT / Konveksi — % WIP Jadi & Kirim")
    if not st.session_state.rolls: st.warning("Belum ada Roll"); st.stop()
    if len(st.session_state.wip)!=len(st.session_state.rolls):
        st.session_state.wip=[{"roll_serie":r["roll_serie"],"jadi":r["kodi"],"kirim":0.0} for r in st.session_state.rolls]
    tj=0; tk=0
    for i,w in enumerate(st.session_state.wip):
        with st.container(border=True):
            c1,c2,c3,c4=st.columns(4)
            with c1: st.text(w["roll_serie"])
            with c2: w["jadi"]=st.number_input("Jadi",value=w["jadi"],key=f"c_j{i}"); tj+=w["jadi"]
            with c3: w["kirim"]=st.number_input("Kirim",value=w["kirim"],key=f"c_k{i}"); tk+=w["kirim"]
            with c4: st.caption("Balance OK" if w["jadi"]-w["kirim"]==0 else f"Sisa {w['jadi']-w['kirim']:.2f}")
    c1,c2,c3=st.columns(3); c1.metric("% WIP Jadi",f"{tj:.1f}"); c2.metric("Kirim",f"{tk:.1f}"); c3.metric("Balance",f"{tj-tk:.1f}")
    st.text_area("Pesan dan Saran CMT")

# === SUPIR - CUMA BOLEH INI ===
else:
    st.title("SUPIR — GPS & Pengiriman")
    st.caption("Cuma pegang: GPS Maps, Nama/SIM/KTP, No Polisi, Sampai Tujuan")
    if st.session_state.wip: st.metric("Total Kirim", f"{sum(w['kirim'] for w in st.session_state.wip):.1f} Kodi")
    with st.container(border=True):
        c1,c2=st.columns(2)
        with c1:
            st.session_state.supir["nama"]=st.text_input("Supir / Nama / SIM / KTP", st.session_state.supir["nama"])
            st.session_state.supir["nopol"]=st.text_input("No Polisi", st.session_state.supir["nopol"])
        with c2:
            st.session_state.supir["gps"]=st.text_input("GPS Maps Via titik", st.session_state.supir["gps"], placeholder="-6.8731,107.5423")
            if st.session_state.supir["gps"]: st.link_button("📍 Buka GPS", f"https://maps.google.com/?q={st.session_state.supir['gps']}")
    st.session_state.supir["sampai"]=st.checkbox("Sampai tujuan Gedung Direktur", value=st.session_state.supir["sampai"])
    if st.session_state.supir["sampai"]: st.camera_input("Foto Bukti")
    if st.button("Supir diminta alihkan ke CMT → Klik Selesai",type="primary"):
        st.balloons(); st.success("✅ Selesai - Terpantau Direktur")
    st.text_area("Pesan dan Saran Supir")
