import requests
import streamlit as st

API_BASE = "https://movie-rec-466x.onrender.com" or "http://127.0.0.1:8000"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

st.markdown(
    """
<style>
.stApp { background: radial-gradient(ellipse at 50% -18%, #282843 0%, #12131d 48%, #0d0e15 100%); color: #f4f3f8; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1440px; }
[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] { background: #11121b; border-right: 1px solid rgba(255,255,255,.07); }
[data-testid="stSidebar"] > div:first-child { padding-top: 1.5rem; }
h1, h2, h3 { letter-spacing: -.035em; color: #f7f5fb; }
h1 { font-weight: 750; }
p, .stMarkdown, label { color: #d4d2df; }
.eyebrow { color: #ffbd69; text-transform: uppercase; letter-spacing: .18em; font-size: .72rem; font-weight: 750; margin-bottom: .55rem; }
.hero { position: relative; overflow: hidden; padding: 2.4rem 2.7rem; margin: .6rem 0 1.5rem; border: 1px solid rgba(255,255,255,.11); border-radius: 24px; background: linear-gradient(115deg, rgba(70,42,76,.78), rgba(29,32,52,.92) 58%, rgba(22,37,48,.92)); box-shadow: 0 24px 70px rgba(0,0,0,.28); }
.hero:after { content: '✦'; position: absolute; right: 7%; top: -52px; font-size: 17rem; line-height: 1; color: rgba(255,255,255,.045); transform: rotate(15deg); pointer-events: none; }
.hero h1 { margin: 0; font-size: clamp(2.2rem, 5vw, 3.8rem); line-height: 1.05; }
.hero-copy { max-width: 610px; color: #d2cede; font-size: 1.05rem; margin-top: .8rem; }
.small-muted { color: #a6a4b4; font-size: .88rem; }
.section-kicker { color: #ffbd69; text-transform: uppercase; letter-spacing: .14em; font-size: .68rem; font-weight: 750; }
.movie-title { font-size: .95rem; line-height: 1.3rem; min-height: 2.6rem; overflow: hidden; font-weight: 650; color: #f4f3f8; margin: .65rem 0 .3rem; }
[data-testid="stVerticalBlockBorderWrapper"] { border-color: rgba(255,255,255,.10) !important; border-radius: 16px !important; background: rgba(255,255,255,.025); transition: transform .18s ease, border-color .18s ease, background .18s ease; }
[data-testid="stVerticalBlockBorderWrapper"]:hover { border-color: rgba(255,189,105,.48) !important; background: rgba(255,255,255,.045); transform: translateY(-3px); }
[data-testid="stImage"] img { border-radius: 10px; }
.stButton > button { border-radius: 10px; font-weight: 650; transition: all .18s ease; }
.stButton > button[kind="primary"] { background: #f3a94f; color: #21170d; border: 0; }
.stButton > button:hover { border-color: #f3a94f; color: #ffd08e; }
[data-testid="stTextInput"] input, [data-testid="stSelectbox"] > div > div, [data-testid="stSlider"] { border-radius: 10px; }
[data-testid="stAlert"] { border-radius: 12px; }
hr { border-color: rgba(255,255,255,.1); }
.detail-panel { padding: 1.2rem 1.4rem; border: 1px solid rgba(255,255,255,.1); border-radius: 18px; background: rgba(255,255,255,.035); }
.detail-meta { color: #b5b2c2; font-size: .9rem; margin: .4rem 0; }
@media (max-width: 700px) { .block-container { padding: 1rem 1rem 3rem; } .hero { padding: 1.7rem 1.4rem; } }
</style>
""",
    unsafe_allow_html=True,
)

if "view" not in st.session_state:
    st.session_state.view = "home"  
if "selected_tmdb_id" not in st.session_state:
    st.session_state.selected_tmdb_id = None

qp_view = st.query_params.get("view")
qp_id = st.query_params.get("id")
if qp_view in ("home", "details"):
    st.session_state.view = qp_view
if qp_id:
    try:
        st.session_state.selected_tmdb_id = int(qp_id)
        st.session_state.view = "details"
    except:
        pass


def goto_home():
    st.session_state.view = "home"
    st.query_params["view"] = "home"
    if "id" in st.query_params:
        del st.query_params["id"]
    st.rerun()


def goto_details(tmdb_id: int):
    st.session_state.view = "details"
    st.session_state.selected_tmdb_id = int(tmdb_id)
    st.query_params["view"] = "details"
    st.query_params["id"] = str(int(tmdb_id))
    st.rerun()


@st.cache_data(ttl=30)  
def api_get_json(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=25)
        if r.status_code >= 400:
            return None, f"HTTP {r.status_code}: {r.text[:300]}"
        return r.json(), None
    except Exception as e:
        return None, f"Request failed: {e}"


def poster_grid(cards, cols=6, key_prefix="grid"):
    if not cards:
        st.info("No movies to show.")
        return

    rows = (len(cards) + cols - 1) // cols
    idx = 0
    for r in range(rows):
        colset = st.columns(cols)
        for c in range(cols):
            if idx >= len(cards):
                break
            m = cards[idx]
            idx += 1

            tmdb_id = m.get("tmdb_id")
            title = m.get("title", "Untitled")
            poster = m.get("poster_url")

            with colset[c]:
                with st.container(border=True):
                    if poster:
                        st.image(poster, use_container_width=True)
                    else:
                        st.markdown(
                            "<div style='height:250px;display:grid;place-items:center;background:#20212c;border-radius:10px;color:#a6a4b4'>Poster unavailable</div>",
                            unsafe_allow_html=True,
                        )

                    st.markdown(
                        f"<div class='movie-title'>{title}</div>", unsafe_allow_html=True
                    )
                    if st.button("View film", key=f"{key_prefix}_{r}_{c}_{idx}_{tmdb_id}", use_container_width=True):
                        if tmdb_id:
                            goto_details(tmdb_id)


def to_cards_from_tfidf_items(tfidf_items):
    cards = []
    for x in tfidf_items or []:
        tmdb = x.get("tmdb") or {}
        if tmdb.get("tmdb_id"):
            cards.append(
                {
                    "tmdb_id": tmdb["tmdb_id"],
                    "title": tmdb.get("title") or x.get("title") or "Untitled",
                    "poster_url": tmdb.get("poster_url"),
                }
            )
    return cards


def parse_tmdb_search_to_cards(data, keyword: str, limit: int = 24):
    """
    Returns:
      suggestions: list[(label, tmdb_id)]
      cards: list[{tmdb_id,title,poster_url}]
    """
    keyword_l = keyword.strip().lower()

    if isinstance(data, dict) and "results" in data:
        raw = data.get("results") or []
        raw_items = []
        for m in raw:
            title = (m.get("title") or "").strip()
            tmdb_id = m.get("id")
            poster_path = m.get("poster_path")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": f"{TMDB_IMG}{poster_path}" if poster_path else None,
                    "release_date": m.get("release_date", ""),
                }
            )

    elif isinstance(data, list):
        raw_items = []
        for m in data:
            tmdb_id = m.get("tmdb_id") or m.get("id")
            title = (m.get("title") or "").strip()
            poster_url = m.get("poster_url")
            if not title or not tmdb_id:
                continue
            raw_items.append(
                {
                    "tmdb_id": int(tmdb_id),
                    "title": title,
                    "poster_url": poster_url,
                    "release_date": m.get("release_date", ""),
                }
            )
    else:
        return [], []

    matched = [x for x in raw_items if keyword_l in x["title"].lower()]

    final_list = matched if matched else raw_items

    suggestions = []
    for x in final_list[:10]:
        year = (x.get("release_date") or "")[:4]
        label = f"{x['title']} ({year})" if year else x["title"]
        suggestions.append((label, x["tmdb_id"]))

    cards = [
        {"tmdb_id": x["tmdb_id"], "title": x["title"], "poster_url": x["poster_url"]}
        for x in final_list[:limit]
    ]
    return suggestions, cards


with st.sidebar:
    st.markdown("## 🎞️ Cinephile")
    st.caption("Your next favorite film is one search away.")
    if st.button("⌂  Discover movies", use_container_width=True):
        goto_home()

    st.markdown("---")
    st.markdown("### Browse")
    st.caption("Choose a collection for your home feed.")
    home_category = st.selectbox(
        "Category",
        ["trending", "popular", "top_rated", "now_playing", "upcoming"],
        index=0,
        format_func=lambda value: value.replace("_", " ").title(),
    )
    grid_cols = st.slider("Posters per row", 3, 6, 5)


if st.session_state.view == "home":
    st.markdown(
        "<div class='hero'><div class='eyebrow'>The film finder</div><h1>Find your<br>next favorite.</h1><div class='hero-copy'>Explore what’s trending, search the movies you love, and discover what to watch next.</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='section-kicker'>Start exploring</div>", unsafe_allow_html=True)
    typed = st.text_input(
        "Search movies",
        placeholder="Try a movie title: Dune, Batman, The Godfather…",
        label_visibility="collapsed",
    )

    st.markdown("<div class='small-muted'>Search by title and open a film to see its details and recommendations.</div>", unsafe_allow_html=True)
    st.write("")

    if typed.strip():
        if len(typed.strip()) < 2:
            st.caption("Type at least 2 characters for suggestions.")
        else:
            data, err = api_get_json("/tmdb/search", params={"query": typed.strip()})

            if err or data is None:
                st.error(f"Search failed: {err}")
            else:
                suggestions, cards = parse_tmdb_search_to_cards(
                    data, typed.strip(), limit=24
                )

                if suggestions:
                    labels = ["-- Select a movie --"] + [s[0] for s in suggestions]
                    selected = st.selectbox("Suggestions", labels, index=0)

                    if selected != "-- Select a movie --":
                        label_to_id = {s[0]: s[1] for s in suggestions}
                        goto_details(label_to_id[selected])
                else:
                    st.info("No suggestions found. Try another keyword.")

                st.markdown("### Search results")
                poster_grid(cards, cols=grid_cols, key_prefix="search_results")

        st.stop()

    st.markdown(f"### {home_category.replace('_',' ').title()} picks")
    st.markdown("<div class='small-muted'>A handpicked place to start your next movie night.</div>", unsafe_allow_html=True)

    home_cards, err = api_get_json(
        "/home", params={"category": home_category, "limit": 24}
    )
    if err or not home_cards:
        st.error(f"Home feed failed: {err or 'Unknown error'}")
        st.stop()

    poster_grid(home_cards, cols=grid_cols, key_prefix="home_feed")


elif st.session_state.view == "details":
    tmdb_id = st.session_state.selected_tmdb_id
    if not tmdb_id:
        st.warning("No movie selected.")
        if st.button("← Back to Home"):
            goto_home()
        st.stop()

    a, b = st.columns([3, 1])
    with a:
        st.markdown("<div class='section-kicker'>Movie profile</div>", unsafe_allow_html=True)
    with b:
        if st.button("← Back to Discover", use_container_width=True):
            goto_home()

    data, err = api_get_json(f"/movie/id/{tmdb_id}")
    if err or not data:
        st.error(f"Could not load details: {err or 'Unknown error'}")
        st.stop()

    left, right = st.columns([1, 2.3], gap="large")

    with left:
        if data.get("poster_url"):
            st.image(data["poster_url"], use_container_width=True)
        else:
            st.info("Poster unavailable")

    with right:
        st.markdown(f"## {data.get('title','Untitled')}")
        release = data.get("release_date") or "-"
        genres = ", ".join([g["name"] for g in data.get("genres", [])]) or "-"
        st.markdown(
            f"<div class='detail-meta'>◷ &nbsp;{release} &nbsp;&nbsp;·&nbsp;&nbsp; {genres}</div>", unsafe_allow_html=True
        )
        st.markdown("---")
        st.markdown("### The story")
        st.write(data.get("overview") or "No overview available.")

    if data.get("backdrop_url"):
        st.markdown("#### Backdrop")
        st.image(data["backdrop_url"], use_container_width=True)

    st.markdown("---")
    st.markdown("<div class='section-kicker'>Keep watching</div>", unsafe_allow_html=True)
    st.markdown("### Recommended for you")

    title = (data.get("title") or "").strip()
    if title:
        bundle, err2 = api_get_json(
            "/movie/search",
            params={"query": title, "tfidf_top_n": 12, "genre_limit": 12},
        )

        if not err2 and bundle:
            st.markdown("#### Similar in story and style")
            poster_grid(
                to_cards_from_tfidf_items(bundle.get("tfidf_recommendations")),
                cols=grid_cols,
                key_prefix="details_tfidf",
            )

            st.markdown("#### More from these genres")
            poster_grid(
                bundle.get("genre_recommendations", []),
                cols=grid_cols,
                key_prefix="details_genre",
            )
        else:
            st.info("Showing Genre recommendations (fallback).")
            genre_only, err3 = api_get_json(
                "/recommend/genre", params={"tmdb_id": tmdb_id, "limit": 18}
            )
            if not err3 and genre_only:
                poster_grid(
                    genre_only, cols=grid_cols, key_prefix="details_genre_fallback"
                )
            else:
                st.warning("No recommendations available right now.")
    else:
        st.warning("No title available to compute recommendations.")
