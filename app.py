import os
from datetime import datetime, timedelta, timezone

import streamlit as st
from supabase import create_client


# ============================================================
# CONFIG
# ============================================================

st.set_page_config(
    page_title="MarketHub",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

SITE_NAME = "MarketHub"

ADMIN_EMAIL = "marketsaleofficial@gmail.com"

CRYPTO_CURRENCY = "USDT"
CRYPTO_NETWORK = "TRC20"
CRYPTO_ADDRESS = "TRzfCcrUmc212VLEYNYVRKtSuYQSnaiU6T"

# ============================================================
# SUPABASE
# ============================================================

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase credentials are missing.")
    st.info(
        "Add SUPABASE_URL and SUPABASE_KEY to your Render "
        "environment variables."
    )
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# ============================================================
# SESSION STATE
# ============================================================

defaults = {
    "user": None,
    "page": "Home",
    "selected_product": None,
    "selected_plan": None,
    "cart": [],
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# DESIGN
# ============================================================

st.markdown(
    """
<style>

@import url(
'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
);

html, body, [class*="css"] {
    font-family: Inter, sans-serif;
}

.stApp {
    background:
        radial-gradient(
            circle at 5% 0%,
            rgba(99,102,241,.20),
            transparent 30%
        ),
        radial-gradient(
            circle at 95% 5%,
            rgba(14,165,233,.14),
            transparent 28%
        ),
        #070a12;
    color: #f8fafc;
}

.block-container {
    max-width: 1250px;
    padding-top: 1.2rem;
    padding-bottom: 4rem;
}

.hero {
    padding: 65px 42px;
    border-radius: 30px;
    background:
        linear-gradient(
            135deg,
            rgba(30,41,90,.97),
            rgba(9,13,29,.98)
        );
    border: 1px solid rgba(148,163,184,.14);
    box-shadow: 0 25px 80px rgba(0,0,0,.30);
    margin-bottom: 28px;
}

.hero-badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 999px;
    background: rgba(99,102,241,.14);
    color: #a5b4fc;
    border: 1px solid rgba(129,140,248,.25);
    font-size: 12px;
    font-weight: 700;
    letter-spacing: .5px;
}

.hero h1 {
    font-size: 55px;
    line-height: 1.04;
    margin: 18px 0;
    font-weight: 800;
}

.hero p {
    max-width: 700px;
    color: #aeb9d1;
    font-size: 18px;
    line-height: 1.7;
}

.card {
    background: rgba(17,24,39,.88);
    border: 1px solid rgba(148,163,184,.12);
    border-radius: 20px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 12px 35px rgba(0,0,0,.16);
}

.product-card {
    background: #101522;
    border: 1px solid rgba(148,163,184,.12);
    border-radius: 20px;
    padding: 14px;
    margin-bottom: 15px;
}

.price {
    font-size: 24px;
    font-weight: 800;
    color: #a5b4fc;
}

.muted {
    color: #94a3b8;
    font-size: 13px;
}

.section-title {
    font-size: 30px;
    font-weight: 800;
    margin: 35px 0 20px;
}

.plan {
    background: #101522;
    border: 1px solid rgba(148,163,184,.14);
    border-radius: 23px;
    padding: 28px;
    min-height: 330px;
    box-shadow: 0 15px 35px rgba(0,0,0,.15);
}

.plan:hover {
    border-color: rgba(129,140,248,.55);
}

.plan-price {
    font-size: 38px;
    font-weight: 800;
    color: #f8fafc;
}

.crypto-box {
    background:
        linear-gradient(
            145deg,
            rgba(30,41,90,.75),
            rgba(12,17,30,.96)
        );
    border: 1px solid rgba(129,140,248,.25);
    border-radius: 25px;
    padding: 30px;
}

.address {
    background: #050811;
    border: 1px solid rgba(129,140,248,.15);
    padding: 17px;
    border-radius: 13px;
    word-break: break-all;
    font-family: monospace;
    color: #a5b4fc;
}

.stat {
    background: #111827;
    border: 1px solid rgba(148,163,184,.11);
    border-radius: 18px;
    padding: 22px;
}

.stat-label {
    color: #94a3b8;
    font-size: 12px;
    font-weight: 700;
}

.stat-number {
    font-size: 30px;
    font-weight: 800;
    margin-top: 7px;
}

.success-box {
    padding: 18px;
    border-radius: 15px;
    background: rgba(34,197,94,.09);
    border: 1px solid rgba(34,197,94,.22);
}

.warning-box {
    padding: 18px;
    border-radius: 15px;
    background: rgba(234,179,8,.08);
    border: 1px solid rgba(234,179,8,.22);
}

</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

def go(page):
    st.session_state.page = page
    st.rerun()


def get_profile(user_id):
    try:
        result = (
            supabase
            .table("profiles")
            .select("*")
            .eq("id", user_id)
            .limit(1)
            .execute()
        )

        if result.data:
            return result.data[0]

    except Exception:
        pass

    return None


def profile():
    if not st.session_state.user:
        return None

    return get_profile(st.session_state.user.id)


def is_admin():
    if not st.session_state.user:
        return False

    if st.session_state.user.email.lower() == ADMIN_EMAIL.lower():
        return True

    p = profile()

    return bool(
        p and p.get("role") == "admin"
    )


def is_seller():
    p = profile()

    if not p:
        return False

    return p.get("role") in ["seller", "admin"]


def get_products():
    try:
        result = (
            supabase
            .table("products")
            .select("*")
            .eq("active", True)
            .order("created_at", desc=True)
            .execute()
        )

        return result.data or []

    except Exception as e:
        st.error(f"Could not load products: {e}")
        return []


def get_my_products():
    if not st.session_state.user:
        return []

    try:
        result = (
            supabase
            .table("products")
            .select("*")
            .eq(
                "seller_id",
                st.session_state.user.id
            )
            .order("created_at", desc=True)
            .execute()
        )

        return result.data or []

    except Exception:
        return []


def get_my_subscription():
    if not st.session_state.user:
        return None

    try:
        result = (
            supabase
            .table("subscriptions")
            .select("*")
            .eq(
                "seller_id",
                st.session_state.user.id
            )
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if result.data:
            return result.data[0]

    except Exception:
        pass

    return None


def subscription_active():
    sub = get_my_subscription()

    if not sub:
        return False

    if sub.get("status") != "approved":
        return False

    expires = sub.get("expires_at")

    if not expires:
        return False

    try:
        expiry = datetime.fromisoformat(
            expires.replace("Z", "+00:00")
        )

        if expiry.tzinfo is None:
            expiry = expiry.replace(
                tzinfo=timezone.utc
            )

        return expiry > datetime.now(timezone.utc)

    except Exception:
        return False


def plan_limit():
    sub = get_my_subscription()

    if not sub or sub.get("status") != "approved":
        return 0

    limits = {
        "Starter": 10,
        "Business": 50,
        "Pro": 200,
    }

    return limits.get(
        sub.get("plan"),
        0
    )


def my_product_count():
    return len(get_my_products())


# ============================================================
# NAVIGATION
# ============================================================

nav = st.columns(
    [2.4, 1, 1, 1, 1, 1, 1.3]
)

with nav[0]:
    if st.button(
        "◈ MarketHub",
        use_container_width=True
    ):
        go("Home")

with nav[1]:
    if st.button("Home", use_container_width=True):
        go("Home")

with nav[2]:
    if st.button("Explore", use_container_width=True):
        go("Explore")

with nav[3]:
    if st.button("Pricing", use_container_width=True):
        go("Pricing")

with nav[4]:
    if st.button("Sell", use_container_width=True):
        go("Seller")

with nav[5]:
    if st.button(
        f"🛒 {len(st.session_state.cart)}",
        use_container_width=True
    ):
        go("Cart")

with nav[6]:
    if st.session_state.user:
        if st.button(
            "Account",
            use_container_width=True
        ):
            go("Account")
    else:
        if st.button(
            "Login",
            use_container_width=True
        ):
            go("Login")

st.divider()


# ============================================================
# HOME
# ============================================================

if st.session_state.page == "Home":

    st.markdown(
        """
        <div class="hero">

            <span class="hero-badge">
            MODERN ONLINE MARKETPLACE
            </span>

            <h1>
            Buy. Sell.<br>
            Grow your business.
            </h1>

            <p>
            Discover products from independent sellers,
            or create your own store and put your products
            in front of buyers.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    search = st.text_input(
        "🔎 Search the marketplace",
        placeholder="Search products or categories..."
    )

    st.markdown(
        "<div class='section-title'>Featured Products</div>",
        unsafe_allow_html=True
    )

    products = get_products()

    if search:
        search_text = search.lower()

        products = [
            p for p in products
            if search_text in (
                str(p.get("name", "")) +
                str(p.get("description", "")) +
                str(p.get("category", ""))
            ).lower()
        ]

    if not products:

        st.info(
            "No products have been listed yet."
        )

    else:

        columns = st.columns(4)

        for i, product in enumerate(products[:12]):

            with columns[i % 4]:

                image = product.get("image_url")

                if image:
                    st.image(
                        image,
                        use_container_width=True
                    )
                else:
                    st.markdown(
                        """
                        <div class="product-card"
                        style="height:210px;
                        display:flex;
                        align-items:center;
                        justify-content:center;
                        font-size:65px;">
                        🛍️
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown(
                    f"""
                    <div class="card">

                    <div class="muted">
                    {product.get("category", "General")}
                    </div>

                    <h3>
                    {product.get("name", "Product")}
                    </h3>

                    <div class="price">
                    ${float(product.get("price", 0)):,.2f}
                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(
                    "View Product",
                    key=f"home_view_{product['id']}",
                    use_container_width=True
                ):

                    st.session_state.selected_product = product

                    go("Product")

    st.markdown(
        "<div class='section-title'>Why MarketHub?</div>",
        unsafe_allow_html=True
    )

    a, b, c = st.columns(3)

    with a:
        st.markdown(
            """
            <div class="card">
            <h2>🏪</h2>
            <h3>Your Store</h3>
            <p class="muted">
            Build your seller presence and display
            your products in one place.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with b:
        st.markdown(
            """
            <div class="card">
            <h2>🌎</h2>
            <h3>Reach Buyers</h3>
            <p class="muted">
            Put your products in front of people
            searching the marketplace.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c:
        st.markdown(
            """
            <div class="card">
            <h2>⚡</h2>
            <h3>Simple Selling</h3>
            <p class="muted">
            Choose a monthly listing plan and
            manage your products easily.
            </p>
            </div>
            """,
            unsafe_allow_html=True
        )


# ============================================================
# EXPLORE
# ============================================================

elif st.session_state.page == "Explore":

    st.markdown(
        "<div class='section-title'>Explore Products</div>",
        unsafe_allow_html=True
    )

    search = st.text_input(
        "🔎 Search",
        placeholder="Search products..."
    )

    category = st.selectbox(
        "Category",
        [
            "All",
            "Electronics",
            "Fashion",
            "Home",
            "Beauty",
            "Sports",
            "Books",
            "Vehicles",
            "Other",
        ]
    )

    products = get_products()

    if search:

        text = search.lower()

        products = [
            p for p in products
            if text in (
                str(p.get("name", "")) +
                str(p.get("description", ""))
            ).lower()
        ]

    if category != "All":

        products = [
            p for p in products
            if p.get("category") == category
        ]

    if not products:

        st.info("No matching products.")

    else:

        columns = st.columns(4)

        for i, product in enumerate(products):

            with columns[i % 4]:

                if product.get("image_url"):
                    st.image(
                        product["image_url"],
                        use_container_width=True
                    )

                st.markdown(
                    f"""
                    <div class="card">

                    <div class="muted">
                    {product.get("category", "General")}
                    </div>

                    <h3>
                    {product.get("name")}
                    </h3>

                    <div class="price">
                    ${float(product.get("price", 0)):,.2f}
                    </div>

                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(
                    "View",
                    key=f"explore_{product['id']}",
                    use_container_width=True
                ):

                    st.session_state.selected_product = product

                    go("Product")


# ============================================================
# PRODUCT
# ============================================================

elif st.session_state.page == "Product":

    product = st.session_state.selected_product

    if not product:
        go("Explore")

    if st.button("← Back to Products"):
        go("Explore")

    left, right = st.columns(
        [1.2, 1]
    )

    with left:

        if product.get("image_url"):

            st.image(
                product["image_url"],
                use_container_width=True
            )

        else:

            st.markdown(
                """
                <div class="card"
                style="
                height:420px;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:100px;">
                🛍️
                </div>
                """,
                unsafe_allow_html=True
            )

    with right:

        st.markdown(
            f"<h1>{product.get('name')}</h1>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div class="price">
            ${float(product.get("price", 0)):,.2f}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        st.write(
            product.get(
                "description",
                "No description provided."
            )
        )

        st.write(
            f"**Category:** "
            f"{product.get('category', 'General')}"
        )

        st.write(
            f"**Stock:** "
            f"{product.get('stock', 0)}"
        )

        if st.button(
            "🛒 Add to Cart",
            use_container_width=True
        ):

            st.session_state.cart.append(
                product
            )

            st.success(
                "Product added to cart."
            )


# ============================================================
# CART
# ============================================================

elif st.session_state.page == "Cart":

    st.markdown(
        "<div class='section-title'>Shopping Cart</div>",
        unsafe_allow_html=True
    )

    cart = st.session_state.cart

    if not cart:

        st.info(
            "Your cart is empty."
        )

        if st.button(
            "Browse Products",
            use_container_width=True
        ):
            go("Explore")

    else:

        total = 0

        for i, product in enumerate(cart):

            price = float(
                product.get("price", 0)
            )

            total += price

            st.markdown(
                f"""
                <div class="card">

                <h3>
                {product.get("name")}
                </h3>

                <div class="price">
                ${price:,.2f}
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )

        st.markdown(
            f"""
            <div class="card">
            <h2>Total</h2>
            <div class="price">
            ${total:,.2f}
            </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.button(
            "Clear Cart",
            use_container_width=True
        ):

            st.session_state.cart = []

            st.rerun()


# ============================================================
# PRICING
# ============================================================

elif st.session_state.page == "Pricing":

    st.markdown(
        "<div class='section-title'>Sell on MarketHub</div>",
        unsafe_allow_html=True
    )

    st.write(
        "Choose a monthly plan for your product listings."
    )

    plans = [
    {
        "name": "Starter",
        "price": 5,
        "listings": 10,
        "description": "Perfect for getting started.",
    },
    {
        "name": "Business",
        "price": 15,
        "listings": 50,
        "description": "For growing sellers.",
    },
    {
        "name": "Pro",
        "price": 30,
        "listings": 200,
        "description": "For serious sellers.",
    },
]

columns = st.columns(3)

for i, plan in enumerate(plans):

    with columns[i]:

        st.markdown(
            f"""
            <div class="plan">

                <div class="muted">
                    MARKETPLACE SELLER PLAN
                </div>

                <h2>{plan["name"]}</h2>

                <div class="plan-price">
                    ${plan["price"]}<span style="font-size:15px;">
                    /month</span>
                </div>

                <p class="muted">
                    {plan["description"]}
                </p>

                <p>
                    ✓ {plan["listings"]} product listings
                </p>

                <p>
                    ✓ Seller dashboard
                </p>

                <p>
                    ✓ Product management
                </p>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button(
            f"Choose {plan['name']}",
            key=f"choose_plan_{plan['name']}",
            use_container_width=True,
        ):

            if not st.session_state.user:
                st.warning("Please log in or create an account first.")
                st.session_state.page = "Login"
                st.rerun()

            else:
                st.session_state.selected_plan = plan
                go("Crypto")