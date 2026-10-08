import streamlit as st
import time
import base64
import os
import html
from presets import PRESET_CATEGORIES
from model_engine import SWOTAnalyzer

# ページ設定
st.set_page_config(
    page_title="高校生のための自己SWOTクロス分析 Navigator",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ロゴ画像のbase64取得
def get_image_base64(filepath):
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
            return f"data:image/png;base64,{encoded}"
    return "./teraoka.png"

logo_b64 = get_image_base64("teraoka.png")

# Tailwind CDN & ダークモード用カスタムスタイル
st.markdown("""
<script src="https://cdn.tailwindcss.com"></script>
<style>
    /* 全体背景とフォント */
    .stApp {
        background-color: #0B0F19;
        color: #F1F5F9;
        font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'BIZ UDPGothic', Meiryo, sans-serif;
    }
    
    /* ヘッダーエリア（タイトル左、ロゴ右上に広幅配置） */
    .header-banner {
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        align-items: flex-start;
        padding: 0.5rem 0 1.25rem 0;
        border-bottom: 1px solid #1E293B;
        margin-bottom: 1.5rem;
        gap: 1.25rem;
    }
    @media (min-width: 900px) {
        .header-banner {
            flex-direction: row;
            align-items: center;
        }
    }
    .header-left {
        flex: 1;
    }
    .app-title {
        font-size: 1.8rem;
        font-weight: 800;
        letter-spacing: -0.01em;
        color: #22D3EE;
        margin: 0 0 0.35rem 0;
        line-height: 1.25;
    }
    .app-desc {
        font-size: 0.9rem;
        color: #94A3B8;
        margin: 0;
        line-height: 1.5;
    }

    /* プロフィールカプセル（文章折り返しなし・広幅デザイン） */
    .profile-pill {
        display: flex;
        align-items: center;
        background: #0f172a;
        padding: 10px 24px 10px 14px;
        border-radius: 9999px;
        border: 1px solid #334155;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.45);
        flex-shrink: 0;
        white-space: nowrap;
        cursor: default;
        transition: border-color 0.2s ease;
    }
    .profile-pill:hover {
        border-color: rgba(6, 182, 212, 0.5);
    }
    .profile-avatar {
        width: 52px;
        height: 52px;
        border-radius: 9999px;
        object-fit: cover;
        border: 2px solid rgba(6, 182, 212, 0.4);
        flex-shrink: 0;
    }
    .profile-text {
        text-align: right;
        margin-left: 14px;
        white-space: nowrap;
    }
    .profile-title {
        font-weight: 700;
        font-size: 13.5px;
        color: #22d3ee;
        margin: 0;
        line-height: 1.3;
    }
    .profile-quote {
        font-size: 11px;
        color: #cbd5e1;
        margin: 4px 0 0 0;
        line-height: 1.35;
        white-space: nowrap;
    }

    /* 一段構成の入力フォームブロック */
    .form-block {
        background: #111827;
        border: 1px solid #1F2937;
        border-radius: 12px;
        padding: 1.15rem 1.4rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .form-block-header {
        display: flex;
        align-items: center;
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
    }
    .form-block-desc {
        font-size: 0.85rem;
        color: #94A3B8;
        margin-bottom: 0.75rem;
        line-height: 1.45;
    }

    /* 戦略マトリクスカード */
    .strategy-card {
        border-radius: 14px;
        padding: 1.4rem;
        margin-bottom: 1.25rem;
        border: 1px solid #334155;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
    }
    .badge-label {
        font-size: 0.75rem;
        font-weight: 700;
        padding: 0.25rem 0.65rem;
        border-radius: 9999px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-bottom: 0.5rem;
    }
    
    /* カラーテーマ別 */
    .card-so {
        background: linear-gradient(180deg, rgba(6, 78, 59, 0.25) 0%, rgba(15, 23, 42, 0.7) 100%);
        border-color: #059669;
    }
    .badge-so { background-color: #065F46; color: #6EE7B7; border: 1px solid #059669; }

    .card-st {
        background: linear-gradient(180deg, rgba(30, 58, 138, 0.25) 0%, rgba(15, 23, 42, 0.7) 100%);
        border-color: #2563EB;
    }
    .badge-st { background-color: #1E3A8A; color: #93C5FD; border: 1px solid #2563EB; }

    .card-wo {
        background: linear-gradient(180deg, rgba(146, 64, 14, 0.25) 0%, rgba(15, 23, 42, 0.7) 100%);
        border-color: #D97706;
    }
    .badge-wo { background-color: #78350F; color: #FCD34D; border: 1px solid #D97706; }

    .card-wt {
        background: linear-gradient(180deg, rgba(153, 27, 27, 0.25) 0%, rgba(15, 23, 42, 0.7) 100%);
        border-color: #DC2626;
    }
    .badge-wt { background-color: #7F1D1D; color: #FCA5A5; border: 1px solid #DC2626; }

    /* テキストエリアの調整 */
    .stTextArea textarea {
        background-color: #1E293B !important;
        color: #F8FAFC !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
    }
    .stTextArea textarea:focus {
        border-color: #06B6D4 !important;
        box-shadow: 0 0 0 1px #06B6D4 !important;
    }

    /* フッター */
    .footer-container {
        margin-top: 4rem;
        padding: 2.5rem 0 1.5rem 0;
        border-top: 1px solid #1E293B;
        text-align: center;
        color: #64748B;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# LLM推論エンジンのロード（キャッシュ）
@st.cache_resource(show_spinner="ローカルLLM（Qwen 2.5）を準備中...")
def get_analyzer():
    analyzer = SWOTAnalyzer()
    analyzer.load()
    return analyzer

# セッション状態の初期化
if "strengths" not in st.session_state:
    st.session_state["strengths"] = ""
if "weaknesses" not in st.session_state:
    st.session_state["weaknesses"] = ""
if "opportunities" not in st.session_state:
    st.session_state["opportunities"] = ""
if "threats" not in st.session_state:
    st.session_state["threats"] = ""
if "results" not in st.session_state:
    st.session_state["results"] = None

# ==========================================
# 1. ヘッダーエリア（タイトル左、ロゴ右上に折り返しなしで配置）
# ==========================================
header_html = f"""
<div class="header-banner">
    <div class="header-left">
        <h1 class="app-title">高校生のための自己SWOTクロス分析 Navigator</h1>
        <p class="app-desc">内的特性と外的環境を論理的に掛け合わせ、未来への「自分だけの羅針盤」を創り出す探究学習ツール</p>
    </div>
    <div class="header-right">
        <!-- プロフィール（文章折り返しなし） -->
        <div class="profile-pill flex items-center bg-slate-900/90 py-2.5 px-6 rounded-full border border-slate-700 shadow-xl ml-4 hover:border-cyan-500/50 transition-colors cursor-default whitespace-nowrap">
            <img src="{logo_b64}" onerror="this.src='https://ui-avatars.com/api/?name=Teraoka&background=0f172a&color=fff'" alt="Profile" class="profile-avatar w-13 h-13 rounded-full object-cover border-2 border-cyan-500/30 flex-shrink-0">
            <div class="profile-text text-right ml-4">
                <p class="profile-title font-bold text-sm text-cyan-400 leading-tight">テラオカ電子の自由探究ゼミ</p>
                <p class="profile-quote text-xs text-gray-300 leading-tight mt-1 whitespace-nowrap">自分が価値を置くものに向かって<br>こつこつ努力する姿ほど<br>素晴らしいものはない</p>
            </div>
        </div>
    </div>
</div>
"""
st.markdown(header_html, unsafe_allow_html=True)

# ==========================================
# 2. 理論・仕組み・使い方の詳細解説アコーディオン
# ==========================================
with st.expander("📖 【必読】SWOT分析の理論・ローカルAIの仕組み・使い方ガイド", expanded=False):
    t_tab1, t_tab2, t_tab3 = st.tabs([
        "1. SWOT分析とクロス分析の理論",
        "2. 搭載ローカルLLM（Qwen 2.5）と安全性",
        "3. 本アプリの使い方と探究のステップ"
    ])

    with t_tab1:
        st.markdown("""
        ### ■ SWOT分析とは？ なぜ高校生の自己理解に必要なのか
        **SWOT（スウォット）分析**は、経営学や事業戦略の策定において世界中で活用されている代表的な環境分析フレームワークです。  
        自分自身を「1つのベンチャー企業」や「プロジェクト」に見立てて客観的に分析することで、**自己満足や無力感に陥らない冷静な現状把握**が可能になります。

        #### ① 内部要因（自分自身がコントロールできること）
        - **Strengths（強み）**: あなたが持つ独自の長所、得意なこと、他者から感謝された経験、自然と継続できる習慣。
        - **Weaknesses（弱み）**: 努力しても人一倍エネルギーを消耗すること、苦手なシチュエーション、改善すべき課題。

        #### ② 外部要因（自分ではコントロールできない社会や環境の波）
        - **Opportunities（機会）**: 時代のトレンド、制度改革（新入試・探究重視など）、学校や地域の恵まれた環境など、自分にとって追い風となる要素。
        - **Threats（脅威）**: AI技術の進化によるスキルの陳腐化、競争倍率の上昇、環境変化など、自分にリスクをもたらす逆風。

        ---

        ### ■ 「クロスSWOT分析」が未来の羅針盤を生み出す
        単に4つの要素を並べるだけでは「現状の記録」に過ぎません。  
        **「内的要因」と「外的要因」をマトリクス状に掛け合わせることで、未来への具体的な4つの戦略（Action Plan）が導き出されます。**

        | 象限 | 掛け合わせ | 戦略テーマ | 高校生にとっての意義 |
        | :--- | :--- | :--- | :--- |
        | **SO戦略** | **強み × 機会** | **積極攻勢** (最大の勝ち筋) | 自分の得意分野を活かして、時代のチャンスをどう掴み取るか。推薦入試や探究発表の核となる戦略。 |
        | **ST戦略** | **強み × 脅威** | **差別化・防御** (逆風の克服) | 競争激化やAIの台頭といった逆風に対し、自分の強みを使って他者とどう差別化し、生き残るか。 |
        | **WO戦略** | **弱み × 機会** | **弱点補強・協業** (チャンスの確保) | 弱点がチャンスの足を引っ張らないよう、デジタルツールの活用や仲間との協力でどう補うか。 |
        | **WT戦略** | **弱み × 脅威** | **専守防衛・リスク回避** (致命傷の回避) | 弱みと逆風が重なる「最悪の事態」を避けるため、無理な戦いを手放し、早めに備えるべき守りの戦略。 |
        """)

    with t_tab2:
        st.markdown("""
        ### ■ 搭載されているローカルLLM（Qwen 2.5）について
        本アプリの頭脳には、アリババが開発し世界的なAIベンチマークで極めて高い評価を獲得しているオープンソースLLM**「Qwen 2.5（Instruct版）」**を採用しています。

        #### 特徴と性能
        - **卓越した論理的推論力**: 軽量でありながら、ビジネス戦略や文章構成の論理破綻が少なく、文脈に沿った的確な日本語を出力します。
        - **指示追従性（Instruction Tuning）**: 「2〜3文で簡潔に具体策を述べる」といった複雑な制約条件を正確に遵守します。

        ---

        ### ■ なぜ「完全ローカル推論」なのか？（教育現場における安全性）
        一般的なAIサービス（ChatGPTやクラウドAPIなど）は、入力した内容が外部の巨大なデータセンターへ送信されます。  
        しかし、高校生の自己分析には**「繊細な悩み」「家庭・学校環境」「将来の個人的な希望」など、極めて秘匿性の高い個人情報**が含まれます。

        - **プライバシー完全保護**: あなたが入力した文字は、このPC（サーバー）のメモリ内でのみ処理され、外部のクラウド企業へ送信されることは一切ありません。
        - **通信遮断環境でも動作可能**: インターネット接続が切断されていても、PC内の計算だけでAIが思考・分析を完了します。
        """)

    with t_tab3:
        st.markdown("""
        ### ■ 本アプリの使い方（4つのステップ）
        1. **ステップ1: サンプル例文の参照・選択（任意）**  
           下の「探究カテゴリー選択」から自分の関心（理系、文系、部活動など）に近いものを選ぶと、実践的な例文が入力欄にセットされます。
        2. **ステップ2: 4つの要素を自分の言葉で編集・入力**  
           「強み・弱み・機会・脅威」を、各欄の問いかけをヒントに言語化します。完璧な文章である必要はありません。
        3. **ステップ3: AIクロス分析を実行**  
           「ローカルAIでクロス分析を実行する」ボタンを押すと、4つの戦略が順番に丁寧に導出されます。
        4. **ステップ4: 羅針盤の確認と深掘り対話**  
           生成された4つの戦略を吟味し、最下部の「外部AI壁打ち用プロンプト」を使って、さらに深い対話や面接対策・志望理由書作成へとステップアップします。
        """)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 3. サンプルデータ選択（バリエーション拡充）
# ==========================================
st.markdown("### 🎯 ステップ1: サンプル例文を選択（または直接入力）")
st.caption("高校生活の様々な場面を想定した例文を用意しました。自分に近いカテゴリーを選んで「入力欄に反映」を押すと、叩き台として活用できます。")

preset_cols = st.columns([1, 2, 1])

with preset_cols[0]:
    category_list = list(PRESET_CATEGORIES.keys())
    selected_category = st.selectbox("カテゴリーを選択", category_list, index=0)

with preset_cols[1]:
    pattern_list = list(PRESET_CATEGORIES[selected_category].keys())
    selected_pattern = st.selectbox("具体的なシナリオを選択", pattern_list, index=0)

with preset_cols[2]:
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("📝 この例文を入力欄にセット", use_container_width=True):
        data = PRESET_CATEGORIES[selected_category][selected_pattern]
        st.session_state["strengths"] = data["strengths"]
        st.session_state["weaknesses"] = data["weaknesses"]
        st.session_state["opportunities"] = data["opportunities"]
        st.session_state["threats"] = data["threats"]
        st.session_state["results"] = None  # 前の結果をリセット
        st.success(f"「{selected_category} - {selected_pattern}」をセットしました！")
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 4. 入力フォーム（一段構成：縦並び）
# ==========================================
st.markdown("### ✍️ ステップ2: 4つの要素を入力・編集（一段構成）")
st.caption("客観的な自己理解を深めるため、自分自身のこと（内部要因）と周囲の環境（外部要因）を切り分けて整理しましょう。")

# ① 強み (Strengths)
st.markdown("""
<div class="form-block" style="border-left: 4px solid #10B981;">
    <div class="form-block-header" style="color: #34D399;">
        💪 1. Strengths（強み・得意・自然にできること）
    </div>
    <div class="form-block-desc">
        <b>【客観化の問いかけ】</b> あなたが普段「当たり前にこなしているが、周囲の人から感謝されたり褒められたりすること」は何ですか？<br>
        粘り強さ、几帳面さ、好奇心、チームでの声かけなど、行動の具体例を挙げてみましょう。
    </div>
</div>
""", unsafe_allow_html=True)
strengths_input = st.text_area(
    "強み入力欄",
    value=st.session_state["strengths"],
    placeholder="例: 数学的な論理的思考が得意で、独学でプログラミングを学んでいる。バグの原因を根気強く特定し、解決まで粘り強く取り組める。",
    height=100,
    label_visibility="collapsed"
)

# ② 弱み (Weaknesses)
st.markdown("""
<div class="form-block" style="border-left: 4px solid #F59E0B;">
    <div class="form-block-header" style="color: #FBBF24;">
        🌧️ 2. Weaknesses（弱み・課題・消耗しやすいこと）
    </div>
    <div class="form-block-desc">
        <b>【客観化の問いかけ】</b> 「努力しても人よりエネルギーを激しく消耗すること」や「つい後回しにしてしまう状況」は何ですか？<br>
        自己否定をする必要はありません。自分の性質（完璧主義、慎重すぎる、人前での緊張など）を冷静に把握します。
    </div>
</div>
""", unsafe_allow_html=True)
weaknesses_input = st.text_area(
    "弱み入力欄",
    value=st.session_state["weaknesses"],
    placeholder="例: 自分の考えを言葉で相手にわかりやすく伝えるのが苦手。興味のない科目の単純暗記は集中力が続かない。",
    height=100,
    label_visibility="collapsed"
)

# ③ 機会 (Opportunities)
st.markdown("""
<div class="form-block" style="border-left: 4px solid #3B82F6;">
    <div class="form-block-header" style="color: #60A5FA;">
        🚀 3. Opportunities（機会・追い風・外部のチャンス）
    </div>
    <div class="form-block-desc">
        <b>【客観化の問いかけ】</b> あなたを取り巻く環境の中で「自分にとって有利に働きそうな社会トレンドや学校の仕組み」は何ですか？<br>
        新入試制度、探究活動の評価、ICTツールの普及、地域の支援プログラムなど、外の世界のチャンスに目を向けます。
    </div>
</div>
""", unsafe_allow_html=True)
opportunities_input = st.text_area(
    "機会入力欄",
    value=st.session_state["opportunities"],
    placeholder="例: 「情報I」の必修化やAI人材への需要増。全国規模のプログラミングコンテストや探究イベントが多数開催されている。",
    height=100,
    label_visibility="collapsed"
)

# ④ 脅威 (Threats)
st.markdown("""
<div class="form-block" style="border-left: 4px solid #EF4444;">
    <div class="form-block-header" style="color: #F87171;">
        ⚡ 4. Threats（脅威・逆風・周囲のリスク）
    </div>
    <div class="form-block-desc">
        <b>【客観化の問いかけ】</b> 自分の意志ではコントロールできない「外の厳しい変化やリスク」は何ですか？<br>
        AIの進化による定型作業の代替、志望学部の倍率上昇、入試制度の変更など、直面しうる障壁を客観的に認識します。
    </div>
</div>
""", unsafe_allow_html=True)
threats_input = st.text_area(
    "脅威入力欄",
    value=st.session_state["threats"],
    placeholder="例: AIの急速な進化による初歩的コーディングの価値低下。理工系学部の人気が高まり、大学入試の倍率が上昇している。",
    height=100,
    label_visibility="collapsed"
)

# セッション状態同期
st.session_state["strengths"] = strengths_input
st.session_state["weaknesses"] = weaknesses_input
st.session_state["opportunities"] = opportunities_input
st.session_state["threats"] = threats_input

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 5. 分析実行ボタン
# ==========================================
action_col1, action_col2 = st.columns([1, 1])
with action_col1:
    analyze_button = st.button("🚀 ローカルAIでクロス分析を実行する（未来の羅針盤を導出）", type="primary", use_container_width=True)
with action_col2:
    if st.button("🔄 入力内容をクリア", use_container_width=True):
        st.session_state["strengths"] = ""
        st.session_state["weaknesses"] = ""
        st.session_state["opportunities"] = ""
        st.session_state["threats"] = ""
        st.session_state["results"] = None
        st.rerun()

# 4つ順番に分析推論処理（確実に途切れず最後まで出力）
if analyze_button:
    if not (strengths_input and weaknesses_input and opportunities_input and threats_input):
        st.warning("⚠️ 4つの項目（強み・弱み・機会・脅威）をすべて入力してください。（ステップ1の例文セットからもすぐにお試しいただけます）")
    else:
        with st.status("🧠 ローカルLLM（Qwen 2.5）が4つの戦略を順番に導出中...", expanded=True) as status:
            analyzer = get_analyzer()
            start_t = time.time()

            # 1. SO戦略
            status.write("⏳ 1/4: SO戦略（積極攻勢：強み × 機会）を導出中...")
            so_text = analyzer.generate_single_strategy(
                strategy_name="【SO戦略（積極攻勢・機会最大化）】",
                factor_a_label="強み(S)",
                factor_a_val=strengths_input,
                factor_b_label="機会(O)",
                factor_b_val=opportunities_input,
                direction_guide="自分の強みを最大限に活かし、追い風やチャンスを掴み取る攻めの具体策"
            )

            # 2. ST戦略
            status.write("⏳ 2/4: ST戦略（差別化：強み × 脅威）を導出中...")
            st_text = analyzer.generate_single_strategy(
                strategy_name="【ST戦略（差別化・脅威回避）】",
                factor_a_label="強み(S)",
                factor_a_val=strengths_input,
                factor_b_label="脅威(T)",
                factor_b_val=threats_input,
                direction_guide="強みを発揮して逆風やリスクを乗り越え、自分ならではの独自の価値で差別化する具体策"
            )

            # 3. WO戦略
            status.write("⏳ 3/4: WO戦略（弱点補強：弱み × 機会）を導出中...")
            wo_text = analyzer.generate_single_strategy(
                strategy_name="【WO戦略（弱点補強・協業推進）】",
                factor_a_label="弱み(W)",
                factor_a_val=weaknesses_input,
                factor_b_label="機会(O)",
                factor_b_val=opportunities_input,
                direction_guide="弱点に足を引っ張られないよう、他者との協調やツールの活用で好機を逃さない工夫"
            )

            # 4. WT戦略
            status.write("⏳ 4/4: WT戦略（専守防衛：弱み × 脅威）を導出中...")
            wt_text = analyzer.generate_single_strategy(
                strategy_name="【WT戦略（専守防衛・リスク回避）】",
                factor_a_label="弱み(W)",
                factor_a_val=weaknesses_input,
                factor_b_label="脅威(T)",
                factor_b_val=threats_input,
                direction_guide="弱みと逆風が重なる致命傷を避けるため、無理を手放し冷静にリスクを回避する防衛策"
            )

            st.session_state["results"] = {
                "SO": so_text,
                "ST": st_text,
                "WO": wo_text,
                "WT": wt_text
            }
            elapsed = time.time() - start_t
            status.update(label=f"✅ 4つの戦略すべての導出が完了しました！（所要時間: {elapsed:.1f}秒）", state="complete", expanded=False)

# ==========================================
# 6. 分析結果の表示（一段構成マトリクスカード）
# ==========================================
if st.session_state["results"]:
    st.markdown("<br><hr style='border-color: #1E293B;'><br>", unsafe_allow_html=True)
    st.markdown("### 🧭 ステップ3: 導き出された『4つの羅針盤（クロス戦略）』")
    st.caption("AIがあなたの内的要因と外的環境を論理的に掛け合わせ、進路・探究活動で実践できるアクションプランを提案しました。")

    res = st.session_state["results"]

    # SO戦略
    st.markdown(f"""
    <div class="strategy-card card-so">
        <span class="badge-label badge-so">SO戦略（積極攻勢・機会最大化）</span>
        <h4 style="color: #6EE7B7; margin-top: 0; font-size: 1.15rem; font-weight: 700;">
            🔥 【強み × 機会】長所を最大限に活かし、追い風やチャンスを掴み取る最大の勝ち筋
        </h4>
        <div style="color: #ECFDF5; font-size: 1rem; line-height: 1.7; margin-top: 0.75rem;">
            {html.escape(res['SO'])}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ST戦略
    st.markdown(f"""
    <div class="strategy-card card-st">
        <span class="badge-label badge-st">ST戦略（差別化・脅威回避）</span>
        <h4 style="color: #93C5FD; margin-top: 0; font-size: 1.15rem; font-weight: 700;">
            🛡️ 【強み × 脅威】強みを発揮して逆風を跳ね返し、自分ならではの価値で差別化する
        </h4>
        <div style="color: #EFF6FF; font-size: 1rem; line-height: 1.7; margin-top: 0.75rem;">
            {html.escape(res['ST'])}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # WO戦略
    st.markdown(f"""
    <div class="strategy-card card-wo">
        <span class="badge-label badge-wo">WO戦略（弱点補強・協業推進）</span>
        <h4 style="color: #FCD34D; margin-top: 0; font-size: 1.15rem; font-weight: 700;">
            🤝 【弱み × 機会】弱点を克服・補強し、仲間やツールの力を借りて好機を逃さない工夫
        </h4>
        <div style="color: #FFFBEB; font-size: 1rem; line-height: 1.7; margin-top: 0.75rem;">
            {html.escape(res['WO'])}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # WT戦略
    st.markdown(f"""
    <div class="strategy-card card-wt">
        <span class="badge-label badge-wt">WT戦略（専守防衛・リスク回避）</span>
        <h4 style="color: #FCA5A5; margin-top: 0; font-size: 1.15rem; font-weight: 700;">
            ⚠️ 【弱み × 脅威】最悪のシナリオ（致命傷）を回避するため、無理を手放し冷静に守る
        </h4>
        <div style="color: #FEF2F2; font-size: 1rem; line-height: 1.7; margin-top: 0.75rem;">
            {html.escape(res['WT'])}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ==========================================
    # 7. AI壁打ち用プロンプト自動生成 & 保存
    # ==========================================
    st.markdown("<br><hr style='border-color: #1E293B;'><br>", unsafe_allow_html=True)
    st.markdown("### 💬 ステップ4: さらに深く探究するための『AI壁打ちプロンプト』")
    st.caption("この分析結果を元に、ChatGPTやGemini等に貼り付けて「志望理由書のブラッシュアップ」や「面接シミュレーション」を行うための構造化プロンプトです。")

    export_markdown = f"""# 高校生のための自己SWOTクロス分析 シート（自分だけの羅針盤）

## 1. 私の現状把握（SWOTデータ）
- **Strengths（強み）**: {strengths_input}
- **Weaknesses（弱み）**: {weaknesses_input}
- **Opportunities（機会）**: {opportunities_input}
- **Threats（脅威）**: {threats_input}

## 2. 導出された4つのクロス戦略（初期仮説）
- **【SO戦略（積極攻勢）】**: {res['SO']}
- **【ST戦略（差別化）】**: {res['ST']}
- **【WO戦略（弱点補強）】**: {res['WO']}
- **【WT戦略（専守防衛）】**: {res['WT']}

---

## 3. 探究メンターAIへの相談・壁打ちプロンプト
```text
あなたは高校生の進路指導および総合型選抜・キャリア探究に精通したプロフェッショナルメンターです。
上記の私の自己SWOTクロス分析データと4つの初期戦略を精読した上で、以下の3つの観点から客観的かつ建設的なフィードバックをください。

1. 【客観性の検証】私が自分自身を過大評価または過小評価している盲点（バイアス）はありませんか？
2. 【今週できるアクション】高校生が明日から無理なく着手できる、具体的で小さなファーストステップを3つ提案してください。
3. 【志望理由・面接への接続】この4つの戦略のうち、志望理由書や自己PRで最も魅力的なエピソードになりそうな核はどこですか？
```
"""

    st.text_area("📋 コピペ用プロンプト", value=export_markdown, height=220)

    down_col1, down_col2 = st.columns([1, 2])
    with down_col1:
        st.download_button(
            label="📥 羅針盤シート（Markdown）を保存する",
            data=export_markdown,
            file_name="highschool_swot_compass.md",
            mime="text/markdown",
            use_container_width=True
        )

# ==========================================
# 8. フッター（要件⑥）
# ==========================================
footer_html = """
<div class="footer-container">
    <div style="font-size: 0.95rem; font-weight: 600; color: #94A3B8; margin-bottom: 0.5rem;">
        高校生のための自己SWOTクロス分析 Navigator
    </div>
    <div style="font-size: 0.8rem; color: #64748B; margin-bottom: 0.75rem;">
        企画・制作：テラオカ電子の自由探究ゼミ / 完全オンデバイスLLM推論（プライバシー保護設計）
    </div>
    <div style="font-size: 0.75rem; color: #475569;">
        自分が価値を置くものに向かって こつこつ努力する姿ほど 素晴らしいものはない
    </div>
    <div style="margin-top: 1rem; font-size: 0.8rem; color: #94A3B8; font-weight: 500;">
        &copy; 2026 Teraoka-Denshi. All rights reserved.
    </div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
