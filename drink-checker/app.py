import streamlit as st
import pandas as pd



from pathlib import Path
import streamlit as st, pandas as pd

# 현재 파일(app.py) 위치 기준
BASE_DIR = Path(__file__).parent
sym_path   = BASE_DIR / "data" / "증상별 성분.xlsx"
drink_path = BASE_DIR / "data" / "카페인.xlsx"

# 존재 여부 확인
if not sym_path.exists() or not drink_path.exists():
    st.error("⚠️  data 폴더에 엑셀 파일이 없습니다. "
             "GitHub 레포에 data/증상별 성분.xlsx 와 data/카페인.xlsx 를 올려주세요.")
    st.stop()

sym_df   = pd.read_excel(sym_path)
drink_df = pd.read_excel(drink_path)


# ────────────────────────────────────
# 1) 표시 문구 ↔ 분류 (학생 체감용 문구)
label2cat = {
    "잠이 안 오거나 너무 긴장돼요": "수면·불안·신경과민",
    "심장이 빨리 뛰거나 혈압이 높아요": "심혈관·고혈압",
    "혈당·체중·여드름이 걱정돼요": "혈당·비만·피부",
    "속쓰림·위가 아파요": "위장·위산",
    "배에 가스가 차거나 설사·변비가 있어요": "장·IBS·가스",
    "간·콩팥 건강이 걱정돼요": "간·신장",
    "신장 결석이 있었어요": "신장결석",
    "호르몬 문제(예: 생리 불순·여드름)가 있어요": "호르몬·내분비",
    "갑상샘 기능이 떨어졌어요": "갑상샘",
    "임신 중이거나 모유 수유 중이에요": "임신·수유",
    "65세 이상이에요": "어린이·청소년",
    "알레르기나 천식이 있어요": "알레르기·천식",
    "혈압이 낮거나 혈압약을 먹어요": "저혈압",
    "손발 저림·신경 문제를 겪어요": "신경계"
}
# ────────────────────────────────────
# 2) 사이드바 체크박스
st.sidebar.title("내 증상 체크")
selected_labels = [
    lab for lab in label2cat
    if st.sidebar.checkbox(lab)
]

# ────────────────────────────────────
# 3) 엑셀 데이터 불러오기
sym_path   = "data/증상별 성분.xlsx"
drink_path = "data/카페인.xlsx"

sym_df   = pd.read_excel(sym_path)
drink_df = pd.read_excel(drink_path)

# 공백 제거
sym_df.columns   = sym_df.columns.str.strip()
sym_df["분류"]    = sym_df["분류"].str.strip()
drink_df.columns = drink_df.columns.str.strip()

# 음료명 열 이름 보정
if "음료명" not in drink_df.columns:
    drink_df = drink_df.rename(columns={drink_df.columns[0]: "음료명"})

# ────────────────────────────────────
# 4) ‘결과 보기’ 버튼
if st.button("결과 보기"):
    if not selected_labels:
        st.warning("왼쪽에서 최소 한 가지 증상을 선택해 주세요!")
        st.stop()

    # 4‑1. 분류 매핑
    categories = [label2cat[l] for l in selected_labels]

    # 4‑2. 위험 성분 목록
    danger_ing = (
        sym_df[sym_df["분류"].isin(categories)][["위험 주성분","위험 부성분"]]
        .fillna("").apply(lambda x: x.str.split(","))
        .sum(axis=1).explode().str.strip().unique().tolist()
    )
    danger_ing = [x for x in danger_ing if x]

    # 열 이름 별칭(띄어쓰기·하이픈 오차 교정)
    alias = {"비타민B3":"비타민 B3","비타민B6":"비타민 B6",
             "비타민C":"비타민 C","L-카르니틴":"L‑카르니틴"}
    drink_df = drink_df.rename(columns=alias)
    danger_ing = [alias.get(x, x) for x in danger_ing]

    # 4‑3. 음료 필터링
    cols = [c for c in danger_ing if c in drink_df.columns]
    mask = drink_df[cols].sum(axis=1) > 0 if cols else pd.Series(False, index=drink_df.index)
    bad_drinks  = drink_df.loc[mask, "음료명"].dropna().astype(str).tolist()
    good_drinks = drink_df.loc[~mask,"음료명"].dropna().astype(str).tolist()

    # 4‑4. 결과 출력
    st.error("❌  피해야 할 음료")
    if bad_drinks:
        st.write("\n".join(bad_drinks))
    else:
        st.write("없음")

    st.success("✅  마셔도 괜찮은 음료")
    if good_drinks:
        st.write("\n".join(good_drinks))
    else:
        st.write("없음")
else:
    st.info("왼쪽에서 증상을 선택한 뒤 [결과 보기]를 눌러 주세요.")
