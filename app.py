import re
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Shopee Smart Assistant (Demo)", page_icon="🛍️", layout="wide")
ROOT = Path(__file__).parent
DATA = ROOT / "data"

@st.cache_data
def load_data():
    p = pd.read_csv(DATA / "products.csv")
    r = pd.read_csv(DATA / "reviews.csv")
    s = pd.read_csv(DATA / "weekly_sales.csv")
    return p, r, s

products, reviews, sales = load_data()

POSITIVE = ["tốt","đẹp","nhanh","thích","hài lòng","ổn định","đáng tiền","tiện lợi","tuyệt vời","thoải mái","bền","lâu"]
NEGATIVE = ["tệ","kém","lỗi","hỏng","chậm","ồn","nhanh hết","không hài lòng","lag","nhỏ","đắt","thất vọng"]

def sentiment(text):
    t = str(text).lower()
    pos = sum(1 for w in POSITIVE if w in t)
    neg = sum(1 for w in NEGATIVE if w in t)
    if pos > neg: return "Tích cực"
    if neg > pos: return "Tiêu cực"
    return "Trung tính"

def money(x):
    return f"{int(x):,}".replace(",", ".") + " đ"

def product_by_name(query):
    q = query.lower()
    for _, row in products.iterrows():
        if row["name"].lower() in q or row["product_id"].lower() in q:
            return row
    # Match broad category keywords
    if "tai nghe" in q:
        return None
    return None

def find_products(query):
    q = query.lower()
    df = products.copy()
    # Extract price limit from common Vietnamese phrasing
    m = re.search(r"(?:dưới|nhỏ hơn|ít hơn|tối đa|không quá)\s*(\d+(?:[.,]\d+)?)\s*(triệu|tr|k|nghìn|ngàn)?", q)
    if m:
        n = float(m.group(1).replace(",", "."))
        unit = m.group(2) or ""
        if unit in ("triệu","tr"): limit = n * 1_000_000
        elif unit in ("k","nghìn","ngàn"): limit = n * 1_000
        else: limit = n if n >= 10000 else n * 1_000_000
        df = df[df["price_vnd"] <= limit]
    if any(w in q for w in ["tai nghe","bluetooth","nghe nhạc"]):
        df = df[df["category"].str.contains("Tai nghe", case=False)]
    elif any(w in q for w in ["chuột","mouse","bàn phím","keyboard"]):
        df = df[df["category"].str.contains("máy tính", case=False)]
    elif any(w in q for w in ["sạc dự phòng","sạc"]):
        df = df[df["category"].str.contains("điện thoại", case=False)]
    return df

def get_reviews(row):
    return reviews[reviews["product_id"] == row["product_id"]].copy()

def review_summary(row):
    rs = get_reviews(row)
    if rs.empty:
        return "Mình chưa có đánh giá mẫu cho sản phẩm này."
    rs["sentiment"] = rs["review_text"].apply(sentiment)
    counts = rs["sentiment"].value_counts()
    total = len(rs)
    summary = ", ".join([f"{k}: {counts.get(k,0)}/{total}" for k in ["Tích cực","Trung tính","Tiêu cực"]])
    examples = "\n".join([f"- ({x['sentiment']}) {x['review_text']}" for _,x in rs.iterrows()])
    return f"Trong {total} đánh giá mẫu: {summary}.\n\nMột số nội dung:\n{examples}"

def forecast(row):
    hist = sales[sales["product_id"] == row["product_id"]].sort_values("week")
    if len(hist) < 4:
        return None, None, "Chưa đủ dữ liệu bán hàng để dự báo."
    # baseline forecast: mean of latest 3 weeks; compare with mean of previous 3
    vals = hist["units_sold"].astype(float).tolist()
    predicted = sum(vals[-3:]) / 3
    prior = sum(vals[-6:-3]) / 3 if len(vals) >= 6 else sum(vals[:-3]) / max(1,len(vals[:-3]))
    if prior == 0: change = 0
    else: change = (predicted-prior)/prior*100
    trend = "tăng" if change > 3 else ("giảm" if change < -3 else "tương đối ổn định")
    return round(predicted,1), round(change,1), f"Dự báo mốc tuần kế tiếp khoảng {predicted:.1f} sản phẩm (trung bình 3 tuần gần nhất). So với 3 tuần trước đó, mức trung bình gần đây {trend} {abs(change):.1f}%."

def respond(query):
    q = query.strip()
    if not q:
        return "Bạn hãy nhập câu hỏi nhé."
  out_of_scope = ["thời tiết","mưa","nắng","nhiệt độ","dự báo thời tiết","trời mưa","trời nắng","bão","lạnh","nóng","bầu cử","chính trị","đau bụng","kết quả bóng đá","tỷ giá"]
    if any(w in q.lower() for w in out_of_scope):
        return "Mình là chatbot demo hỗ trợ tìm sản phẩm, xem đánh giá và dự báo nhu cầu từ dữ liệu mẫu. Mình chưa hỗ trợ chủ đề này."
    row = product_by_name(q)
    if any(w in q.lower() for w in ["dự báo","xu hướng","nhu cầu","tuần sau","bán chạy"]) and row is not None:
        pred, change, msg = forecast(row)
        return f"**{row['name']}**\n\n{msg}\n\nLưu ý: đây là dự báo thử nghiệm từ dữ liệu bán hàng giả lập, không phải dữ liệu thực tế của Shopee."
    if any(w in q.lower() for w in ["đánh giá","review","nhận xét","phàn nàn","cảm xúc"]) and row is not None:
        return f"**Tóm tắt review của {row['name']}**\n\n{review_summary(row)}\n\nLưu ý: sentiment trong bản demo dùng bộ từ khóa đơn giản, có thể phân loại sai."
    if row is not None:
        rs = get_reviews(row)
        avg_sent = rs["review_text"].apply(sentiment).value_counts().to_dict() if not rs.empty else {}
        return (f"**{row['name']}**\n\n"
                f"- Mã sản phẩm: {row['product_id']}\n"
                f"- Danh mục: {row['category']}\n"
                f"- Giá mẫu: {money(row['price_vnd'])}\n"
                f"- Điểm đánh giá mẫu: {row['rating']}/5\n"
                f"- Pin công bố trong dữ liệu mẫu: {int(row['battery_hours'])} giờ\n"
                f"- Trạng thái mẫu: {row['stock_status']}\n\n"
                "Bạn có thể hỏi tiếp về review hoặc dự báo nhu cầu của sản phẩm này.\n\n"
                "Lưu ý: toàn bộ thông tin trên là dữ liệu minh họa do nhóm chuẩn bị.")
    found = find_products(q)
    if not found.empty and any(w in q.lower() for w in ["tìm","có","dưới","giá","tai nghe","chuột","bàn phím","sạc"]):
        lines=[]
        for _,r in found.head(8).iterrows():
            lines.append(f"- **{r['name']}** — {money(r['price_vnd'])}; đánh giá {r['rating']}/5; mã {r['product_id']}")
        return "Mình tìm thấy các sản phẩm trong dữ liệu mẫu:\n\n" + "\n".join(lines) + "\n\nBạn có thể hỏi chi tiết bằng tên sản phẩm hoặc mã sản phẩm."
    return ("Mình chưa xác định được sản phẩm hoặc ý định của câu hỏi. Bạn thử hỏi theo một trong các cách sau:\n"
            "- “Tìm tai nghe dưới 500 nghìn”\n"
            "- “Thông tin Tai nghe Bluetooth A”\n"
            "- “Review Tai nghe Bluetooth A”\n"
            "- “Dự báo nhu cầu Tai nghe Bluetooth A tuần sau”")

st.title("🛍️ Shopee Smart Assistant")
st.caption("Chatbot demo phục vụ bài tập — không phải chatbot chính thức của Shopee.")
with st.sidebar:
    st.header("Chức năng")
    st.markdown("- Tìm kiếm sản phẩm mẫu\n- Truy xuất review\n- Phân tích cảm xúc cơ bản\n- Dự báo nhu cầu bằng trung bình \n- Xử lý câu hỏi ngoài phạm vi")
    st.warning("Dữ liệu sản phẩm, review và doanh số trong bản demo đều là dữ liệu giả lập. Không đại diện cho Shopee.")
    st.header("Ví dụ câu hỏi")
    examples = [
        "Tìm tai nghe dưới 500 nghìn",
        "Thông tin Tai nghe Bluetooth A",
        "Review Tai nghe Bluetooth A",
        "Dự báo nhu cầu Tai nghe Bluetooth A tuần sau",
        "Ngày mai Hà Nội có mưa không?"
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state["pending_query"] = ex

if "messages" not in st.session_state:
    st.session_state.messages = [{"role":"assistant","content":"Xin chào! Mình có thể giúp bạn tìm sản phẩm mẫu, đọc review hoặc dự báo nhu cầu. Bạn muốn tìm gì?"}]
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

pending = st.session_state.pop("pending_query", None)
prompt = st.chat_input("Nhập câu hỏi về sản phẩm...")
if pending:
    prompt = pending
if prompt:
    st.session_state.messages.append({"role":"user","content":prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    answer = respond(prompt)
    st.session_state.messages.append({"role":"assistant","content":answer})
    with st.chat_message("assistant"):
        st.markdown(answer)

st.divider()
st.subheader("Dữ liệu mẫu")
col1,col2,col3 = st.columns(3)
col1.metric("Sản phẩm", len(products))
col2.metric("Đánh giá", len(reviews))
col3.metric("Điểm dữ liệu doanh số", len(sales))
with st.expander("Xem bảng sản phẩm"):
    st.dataframe(products, use_container_width=True, hide_index=True)
with st.expander("Xem bảng review và nhãn cảm xúc"):
    rv = reviews.copy()
    rv["sentiment_demo"] = rv["review_text"].apply(sentiment)
    st.dataframe(rv, use_container_width=True, hide_index=True)
with st.expander("Xem dữ liệu doanh số theo tuần"):
    st.dataframe(sales, use_container_width=True, hide_index=True)
