import streamlit as st
import pandas as pd
from pathlib import Path

# ──────────────────────────────
# 1) 파일 경로 (data 폴더 안)
BASE_DIR = Path(__file__).parent
SYM_PATH = BASE_DIR / "data" / "symptoms.xlsx"
DRINK_PATH = BASE_DIR / "data" / "caffeine.xlsx"

# 파일 존재 확인
if not (SYM_PATH.exists() and DRINK_PATH.exists()):
    st.error(
        "data 폴더 안에 symptoms.xlsx / caffeine.xlsx 파일이 없습니다.\n"
        "폴더 구조가 정확한지 확인해 주세요."
    )
    st.stop()

# ──────────────────────────────
# 2) 데이터 불러오기 & 공백 제거
sym_df   = pd.read_excel(SYM_PATH)
drink_df = pd.read_excel(DRINK_PATH)

sym_df.columns   = sym_df.columns.str.strip()
drink_df.columns = drink_df.columns.str.strip()
sym_df["분류"]    = sym_df["분류"].str.strip()
if "음료명" not in drink_df.columns:
    drink_df = drink_df.rename(columns={drink_df.columns[0]: "음료명"})

# ──────────────────────────────
# 3) 학생용 체크 문구 ↔ 분류 매핑
label2cat = {
    "잠이 안 오거나 너무 긴장돼요"            : "수면·불안·신경과민",
    "심장이 빨리 뛰거나 혈압이 높아요"        : "심혈관·고혈압",
    "혈당·체중·여드름이 걱정돼요"             : "혈당·비만·피부",
    "속쓰림·위가 아파요"                    : "위장·위산",
    "배에 가스가 차거나 설사·변비가 있어요"  : "장·IBS·가스",
    "간·콩팥 건강이 걱정돼요"               : "간·신장",
    "신장 결석이 있었어요"                 : "신장결석",
    "호르몬 문제(예: 생리 불순·여드름)가 있어요": "호르몬·내분비",
    "갑상샘 기능이 떨어졌어요"              : "갑상샘",
    "임신 중이거나 모유 수유 중이에요"        : "임신·수유",
    "65세 이상"                  : "어린이·청소년",
    "알레르기나 천식이 있어요"              : "알레르기·천식",
    "혈압이 낮거나 혈압약을 먹어요"          : "저혈압",
    "손발 저림·신경 문제를 겪어요"          : "신경계"
}

# ──────────────────────────────
# 4) Streamlit UI
st.title("🥤 에너지음료 주의 진단기")
st.sidebar.header("내 증상 체크")

selected_labels = [
    lab for lab in label2cat
    if st.sidebar.checkbox(lab)
]

if st.button("결과 보기"):

    if not selected_labels:
        st.warning("왼쪽에서 최소 한 가지 증상을 선택해 주세요.")
        st.stop()

    # 4‑1) 분류 추출
    categories = [label2cat[l] for l in selected_labels]

    # 4‑2) 위험 성분 목록
    danger_ing = (
        sym_df[sym_df["분류"].isin(categories)][["위험 주성분", "위험 부성분"]]
        .fillna("").apply(lambda x: x.str.split(","))
        .sum(axis=1).explode().str.strip().unique().tolist()
    )
    danger_ing = [d for d in danger_ing if d]

    # 4‑3) 열 이름 보정
    alias = {
        "비타민B3": "비타민 B3",
        "비타민B6": "비타민 B6",
        "비타민C":  "비타민 C",
        "L-카르니틴": "L‑카르니틴"
    }
    drink_df = drink_df.rename(columns=alias)
    danger_ing = [alias.get(x, x) for x in danger_ing]

    # 4‑4) 음료 필터링
    cols_exist = [c for c in danger_ing if c in drink_df.columns]
    mask = drink_df[cols_exist].sum(axis=1) > 0 if cols_exist else pd.Series(False, index=drink_df.index)
    bad  = drink_df.loc[mask, "음료명"].dropna().astype(str).tolist()
    good = drink_df.loc[~mask, "음료명"].dropna().astype(str).tolist()

    # ─ 결과 출력 ─
    st.error("❌ 피해야 할 음료")
    st.write("\n".join(bad) if bad else "없음")

    st.success("✅ 마셔도 괜찮은 음료")
    st.write("\n".join(good) if good else "없음")

else:
    st.info("왼쪽에서 증상을 선택하고 [결과 보기] 버튼을 눌러 주세요.")
