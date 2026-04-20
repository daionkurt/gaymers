from __future__ import annotations

from datetime import date, datetime
from io import BytesIO
import json
import os
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from PIL import Image, ImageOps

from database import (
    create_member,
    delete_member,
    get_database_backend,
    get_member,
    init_db,
    list_members,
    update_member,
)

PAGE_TITLE = "Directorio Gaymers MX-GDL"
NAV_OPTIONS = ["Resumen", "Cumpleaños", "Nuevo miembro", "Directorio", "Perfil"]
SEXUALITY_OPTIONS = [
    "",
    "Gay",
    "Bisexual",
    "Pansexual",
    "Asexual",
    "Queer",
    "Otro",
]
MUSIC_OPTIONS = [
    "Pop",
    "Girly",
    "Rock",
    "Indie",
    "K-pop",
    "Electro",
    "Daft Punk",
    "Reggaeton",
    "Metal",
    "Techno",
    "Trap",
    "Baladas",
    "Regional mexicano",
    "Jazz",
    "Clasica",
    "Rap",
    "Banda",
    "Narco-corridos",
    "En español",
    "En inglés"
]
GAMING_SYSTEM_OPTIONS = [
    "PS4",
    "PS5",
    "Xbox One",
    "Xbox Series X|S",
    "PC",
    "Nintendo Switch",
    "Nintendo Switch 2",
    "Celular",
    "Steam Deck",
    "Retro",
]
DAY_OPTIONS = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo"]
TIME_OPTIONS = [
    "Madrugada",
    "Manana",
    "Tarde",
    "Noche",
    "Late night",
    "Flexible",
]
MONTH_NAMES_ES = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}
ASSETS_DIR = Path(__file__).parent / "assets"
BANNER_PATH = ASSETS_DIR / "gaymers_banner.svg"
BIRTHDAY_BANNER_PATH = ASSETS_DIR / "birthday_gamer_banner.svg"
BIRTHDAY_MIN_DATE = date(1950, 1, 1)
BIRTHDAY_MAX_DATE = date(2100, 12, 31)
PLATFORM_ICON_MAP = {
    "PS4": "🎮",
    "PS5": "🎮",
    "Xbox One": "🟢",
    "Xbox Series X|S": "🟢",
    "PC": "💻",
    "Nintendo Switch": "🕹️",
    "Nintendo Switch 2": "🕹️",
    "Celular": "📱",
    "Steam Deck": "🎛️",
    "Retro": "👾",
}


def initialize_app() -> None:
    st.set_page_config(page_title=PAGE_TITLE, layout="wide")
    init_db()
    apply_black_theme()

    if "pending_view" in st.session_state:
        st.session_state["current_view"] = st.session_state.pop("pending_view")

    if "current_view" not in st.session_state:
        st.session_state["current_view"] = "Resumen"

    if "selected_member_id" not in st.session_state:
        st.session_state["selected_member_id"] = None

    if "admin_session_member_id" not in st.session_state:
        st.session_state["admin_session_member_id"] = None

    if "admin_unlocked" not in st.session_state:
        st.session_state["admin_unlocked"] = False

    if "flash_message" not in st.session_state:
        st.session_state["flash_message"] = None


def apply_black_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --app-bg: #050505;
            --panel-bg: #111111;
            --panel-border: #262626;
            --text-main: #f5f5f5;
            --text-soft: #cfcfcf;
        }

        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"],
        [data-testid="stToolbar"] {
            background: var(--app-bg) !important;
            color: var(--text-main) !important;
        }

        [data-testid="stSidebar"] {
            background: #090909 !important;
        }

        [data-testid="stSidebar"] * {
            color: var(--text-main) !important;
        }

        [data-testid="stMetric"],
        [data-testid="stForm"],
        [data-testid="stExpander"],
        [data-testid="stDataFrame"],
        div[data-testid="stVerticalBlock"] div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlockBorderWrapper"],
        div[data-testid="stContainer"] {
            color: var(--text-main) !important;
        }

        [data-testid="stDataFrame"],
        [data-testid="stFileUploaderDropzone"],
        [data-testid="stExpander"],
        [data-testid="stForm"] {
            background: var(--panel-bg) !important;
            border: 1px solid var(--panel-border) !important;
            box-shadow: none !important;
            border-radius: 0.8rem !important;
            color: var(--text-main) !important;
        }

        div[data-baseweb="select"] > div,
        div[data-baseweb="base-input"] > div,
        div[data-baseweb="input"] > div,
        div[data-baseweb="textarea"] > div,
        .stTextInput > div > div,
        .stDateInput > div > div,
        .stSelectbox > div > div,
        .stMultiSelect > div > div,
        .stTextArea > div > div {
            background: var(--panel-bg) !important;
            border: 1px solid var(--panel-border) !important;
            box-shadow: none !important;
            border-radius: 0.8rem !important;
            overflow: hidden !important;
        }

        .stTextInput input,
        .stDateInput input,
        .stSelectbox input,
        .stMultiSelect input,
        .stTextArea textarea {
            background: transparent !important;
            border: 0 !important;
            box-shadow: none !important;
            color: var(--text-main) !important;
            caret-color: #ff4fa3 !important;
        }

        .stTextInput > div > div:focus-within,
        .stDateInput > div > div:focus-within,
        .stSelectbox > div > div:focus-within,
        .stMultiSelect > div > div:focus-within,
        .stTextArea > div > div:focus-within,
        div[data-baseweb="select"] > div:focus-within,
        div[data-baseweb="base-input"] > div:focus-within,
        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="textarea"] > div:focus-within {
            border: 1px solid #ff4fa3 !important;
            box-shadow: 0 0 0 1px #ff4fa3 !important;
        }

        [data-baseweb="tag"] {
            background: #ff4fa3 !important;
            border: 0 !important;
            border-radius: 0.6rem !important;
            box-shadow: none !important;
            margin: 0.2rem 0.15rem 0.2rem 0 !important;
            padding: 0.05rem 0.15rem !important;
        }

        [data-baseweb="tag"] * {
            color: #ffffff !important;
            background: transparent !important;
        }

        .rainbow-section-title {
            margin: 0.9rem 0 0.5rem 0;
            font-size: 1.15rem;
            font-weight: 800;
            letter-spacing: 0.04em;
            background: linear-gradient(90deg, #ff4fa3 0%, #ff7a59 22%, #ffd166 46%, #43d17a 68%, #4db8ff 84%, #9b5cff 100%);
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent !important;
            -webkit-text-fill-color: transparent;
            display: inline-block;
        }

        .stTextInput label,
        .stDateInput label,
        .stSelectbox label,
        .stMultiSelect label,
        .stTextArea label {
            margin-bottom: 0.35rem !important;
        }

        .stMarkdown,
        .stCaption,
        .stText,
        p,
        label,
        li,
        h1,
        h2,
        h3,
        h4 {
            color: var(--text-main) !important;
        }

        .stCaption {
            color: var(--text-soft) !important;
        }

        button[kind],
        .stButton > button,
        .stDownloadButton > button {
            background: #181818 !important;
            color: #ffffff !important;
            border: 1px solid #303030 !important;
        }

        .stButton > button:hover,
        .stDownloadButton > button:hover {
            border-color: #ff4fa3 !important;
            color: #ff9bc8 !important;
        }

        .gaymers-rainbow-title {
            margin: 0 0 1.2rem 0;
            font-size: 2rem;
            line-height: 1.5;
            font-weight: 900;
            letter-spacing: 0.18em;
            word-spacing: 0.55em;
            background: linear-gradient(
                90deg,
                #e53935 0%,
                #fb8c00 18%,
                #fdd835 34%,
                #43a047 50%,
                #00acc1 66%,
                #1e88e5 82%,
                #8e24aa 100%
            );
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent !important;
            -webkit-text-fill-color: transparent;
            display: inline-block;
            text-transform: none;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def set_flash(kind: str, message: str) -> None:
    st.session_state["flash_message"] = {"kind": kind, "message": message}


def show_flash() -> None:
    flash = st.session_state.get("flash_message")
    if not flash:
        return

    message = flash["message"]
    kind = flash["kind"]

    if kind == "success":
        st.success(message)
    elif kind == "warning":
        st.warning(message)
    else:
        st.info(message)

    st.session_state["flash_message"] = None


def parse_optional_int(value: str, label: str) -> int | None:
    raw_value = value.strip()
    if not raw_value:
        return None

    try:
        parsed = int(raw_value)
    except ValueError as exc:
        raise ValueError(f"{label} debe ser un numero entero.") from exc

    if parsed < 0:
        raise ValueError(f"{label} no puede ser negativo.")

    return parsed


def parse_optional_choice(value: Any) -> int | None:
    if value in (None, ""):
        return None
    parsed = int(value)
    return parsed


def split_multi_value(value: str | None) -> list[str]:
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def join_multi_value(values: list[str], other_value: str = "") -> str | None:
    combined = [value.strip() for value in values if value.strip()]
    if other_value.strip():
        combined.extend([item.strip() for item in other_value.split(",") if item.strip()])
    if not combined:
        return None
    seen: list[str] = []
    for value in combined:
        if value not in seen:
            seen.append(value)
    return ", ".join(seen)


def parse_json_map(value: str | None) -> dict[str, str]:
    if not value:
        return {}
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        return {}
    if not isinstance(parsed, dict):
        return {}
    return {str(key): str(item) for key, item in parsed.items() if str(item).strip()}


def serialize_platform_ids(values: dict[str, str]) -> str | None:
    clean_values = {key: value.strip() for key, value in values.items() if value and value.strip()}
    if not clean_values:
        return None
    return json.dumps(clean_values, ensure_ascii=True, sort_keys=True)


def parse_platform_ids_for_display(value: str | None) -> list[tuple[str, str]]:
    data = parse_json_map(value)
    return sorted(data.items(), key=lambda item: item[0].lower())


def parse_existing_choice(value: Any, options: list[str]) -> int:
    normalized = "" if value in (None, "") else str(value)
    return options.index(normalized) if normalized in options else 0


def get_banner_path() -> str | None:
    if BANNER_PATH.exists():
        return str(BANNER_PATH)
    return None


def get_birthday_banner_path() -> str | None:
    if BIRTHDAY_BANNER_PATH.exists():
        return str(BIRTHDAY_BANNER_PATH)
    return None


def admin_badge(member: dict[str, Any]) -> str:
    return "" if member.get("is_admin") else ""


def platform_label(system: str) -> str:
    return f"{PLATFORM_ICON_MAP.get(system, '🎲')} {system}"


def render_rainbow_section_title(title: str) -> None:
    st.markdown(f'<div class="rainbow-section-title">{title}</div>', unsafe_allow_html=True)


def render_member_profile_title(member: dict[str, Any]) -> None:
    crown = ""
    if member.get("is_admin"):
        crown = ' <span title="Admin del grupo" style="font-size:0.95em;">👑</span>'

    st.markdown(
        f'<h2 style="margin:0 0 0.35rem 0;">{display_name(member)}{crown}</h2>',
        unsafe_allow_html=True,
    )


def get_admin_pin() -> str | None:
    env_value = os.getenv("ADMIN_PIN")
    if env_value:
        return env_value

    try:
        secret_value = st.secrets.get("ADMIN_PIN")
        if secret_value:
            return str(secret_value)
    except Exception:
        pass

    return None


def get_active_admin_member(members: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not st.session_state.get("admin_unlocked"):
        return None

    admin_id = st.session_state.get("admin_session_member_id")
    if not admin_id:
        return None

    for member in members:
        if member["id"] == admin_id and member.get("is_admin"):
            return member

    st.session_state["admin_session_member_id"] = None
    return None


def is_admin_session_active(members: list[dict[str, Any]]) -> bool:
    return get_active_admin_member(members) is not None


def lock_admin_session() -> None:
    st.session_state["admin_unlocked"] = False
    st.session_state["admin_session_member_id"] = None


def calculate_zodiac_sign(birthday_value: date | None) -> str | None:
    if birthday_value is None:
        return None

    month = birthday_value.month
    day = birthday_value.day

    zodiac_ranges = [
        ((1, 20), (2, 18), "Acuario"),
        ((2, 19), (3, 20), "Piscis"),
        ((3, 21), (4, 19), "Aries"),
        ((4, 20), (5, 20), "Tauro"),
        ((5, 21), (6, 20), "Geminis"),
        ((6, 21), (7, 22), "Cancer"),
        ((7, 23), (8, 22), "Leo"),
        ((8, 23), (9, 22), "Virgo"),
        ((9, 23), (10, 22), "Libra"),
        ((10, 23), (11, 21), "Escorpio"),
        ((11, 22), (12, 21), "Sagitario"),
        ((12, 22), (12, 31), "Capricornio"),
        ((1, 1), (1, 19), "Capricornio"),
    ]

    for start, end, sign in zodiac_ranges:
        if (month, day) >= start and (month, day) <= end:
            return sign

    return None


def format_birthday_for_storage(value: date | None) -> str | None:
    if value is None:
        return None
    return value.isoformat()


def parse_birthday_for_input(value: str | None) -> date | None:
    if not value:
        return None

    try:
        return date.fromisoformat(value)
    except ValueError:
        pass

    normalized = value.strip().lower()
    if " de " in normalized:
        try:
            day_part, month_part = normalized.split(" de ", 1)
            day = int(day_part.strip())
            month_lookup = {name: number for number, name in MONTH_NAMES_ES.items()}
            month = month_lookup.get(month_part.strip())
            if month is not None:
                current_year = datetime.now().year
                return date(current_year, month, day)
        except Exception:
            return None

    return None


def format_birthday_for_display(value: str | None) -> str:
    parsed = parse_birthday_for_input(value)
    if parsed is None:
        return value_or_fallback(value)
    return f"{parsed.day} de {MONTH_NAMES_ES[parsed.month]}"


def get_birthday_month(value: str | None) -> int | None:
    parsed = parse_birthday_for_input(value)
    if parsed is None:
        return None
    return parsed.month


def get_birthday_day(value: str | None) -> int | None:
    parsed = parse_birthday_for_input(value)
    if parsed is None:
        return None
    return parsed.day


def parse_existing_multiselect(value: str | None, allowed_options: list[str]) -> tuple[list[str], str]:
    selected = split_multi_value(value)
    preset = [item for item in selected if item in allowed_options]
    custom = ", ".join(item for item in selected if item not in allowed_options)
    return preset, custom


def format_availability(member: dict[str, Any]) -> str:
    days = member.get("availability_days")
    time_ranges = member.get("availability_time")
    notes = member.get("availability_notes")

    parts = [part for part in [days, time_ranges, notes] if part]
    if not parts:
        return "Sin dato"
    return " | ".join(parts)


def render_platform_id_inputs(prefix: str, existing_values: dict[str, str]) -> dict[str, str]:
    st.caption("IDs de jugador por plataforma. Llena solo los que uses.")
    values: dict[str, str] = {}
    columns = st.columns(2)

    for index, system in enumerate(GAMING_SYSTEM_OPTIONS):
        column = columns[index % 2]
        with column:
            values[system] = st.text_input(
                f"ID en {platform_label(system)}",
                value=existing_values.get(system, ""),
                key=f"{prefix}_platform_id_{index}",
            )

    return values


def process_uploaded_photo(uploaded_file) -> tuple[bytes | None, str | None]:
    if uploaded_file is None:
        return None, None

    image = Image.open(uploaded_file)
    image = ImageOps.exif_transpose(image)
    image.thumbnail((1200, 1200))

    buffer = BytesIO()
    has_alpha = image.mode in {"RGBA", "LA"} or "transparency" in image.info

    if has_alpha:
        image.save(buffer, format="PNG", optimize=True)
        return buffer.getvalue(), "image/png"

    if image.mode != "RGB":
        image = image.convert("RGB")

    image.save(buffer, format="JPEG", quality=85, optimize=True)
    return buffer.getvalue(), "image/jpeg"


def normalize_instagram(handle: str | None) -> str | None:
    if not handle:
        return None
    cleaned = handle.strip()
    if not cleaned:
        return None
    return cleaned[1:] if cleaned.startswith("@") else cleaned


def instagram_url(handle: str | None) -> str | None:
    normalized = normalize_instagram(handle)
    if not normalized:
        return None
    return f"https://www.instagram.com/{normalized}/"


def display_name(member: dict[str, Any]) -> str:
    nickname = member.get("nickname")
    if nickname:
        return f"{admin_badge(member)}{nickname} ({member['full_name']})"
    return f"{admin_badge(member)}{member['full_name']}"


def value_or_fallback(value: Any, fallback: str = "Sin dato") -> str:
    if value in (None, ""):
        return fallback
    return str(value)


def format_date(value) -> str:
    if value is None:
        return "Sin dato"
    return value.strftime("%d/%m/%Y %H:%M")


def open_member_profile(member_id: str) -> None:
    st.session_state["selected_member_id"] = member_id
    st.session_state["pending_view"] = "Perfil"
    st.rerun()


def build_member_payload(
    *,
    full_name: str,
    nickname: str,
    age: Any,
    sexuality: str,
    role: str = "",
    height_cm: Any,
    location: str,
    favorite_color: str,
    favorite_food: str,
    favorite_movies: str,
    music_tastes: list[str],
    music_tastes_other: str,
    hobbies: str,
    favorite_character: str,
    gaming_system: list[str],
    gaming_system_other: str,
    platform_ids: dict[str, str],
    currently_playing: str,
    instagram: str,
    phone: str,
    birthday_value: date | None,
    availability_days: list[str],
    availability_time: list[str],
    availability_notes: str,
    is_admin: bool,
    uploaded_photo,
    existing_member: dict[str, Any] | None = None,
    remove_photo: bool = False,
) -> dict[str, Any]:
    clean_name = full_name.strip()
    if not clean_name:
        raise ValueError("El nombre es obligatorio.")

    parsed_age = parse_optional_choice(age)
    if parsed_age is not None and parsed_age < 10:
        raise ValueError("La edad minima permitida es 10.")

    photo_bytes = existing_member.get("photo_bytes") if existing_member else None
    photo_mime_type = existing_member.get("photo_mime_type") if existing_member else None

    if remove_photo:
        photo_bytes = None
        photo_mime_type = None

    if uploaded_photo is not None:
        photo_bytes, photo_mime_type = process_uploaded_photo(uploaded_photo)

    normalized_birthday = format_birthday_for_storage(birthday_value)

    return {
        "full_name": clean_name,
        "nickname": nickname,
        "age": parsed_age,
        "sexuality": sexuality,
        "role": role,
        "height_cm": parse_optional_choice(height_cm),
        "location": location,
        "favorite_color": favorite_color,
        "favorite_food": favorite_food,
        "favorite_movies": favorite_movies,
        "music_tastes": join_multi_value(music_tastes, music_tastes_other),
        "hobbies": hobbies,
        "zodiac_sign": calculate_zodiac_sign(birthday_value),
        "favorite_character": favorite_character,
        "gaming_system": join_multi_value(gaming_system, gaming_system_other),
        "platform_ids": serialize_platform_ids(platform_ids),
        "currently_playing": currently_playing,
        "instagram": instagram,
        "phone": phone,
        "birthday": normalized_birthday,
        "availability_days": join_multi_value(availability_days),
        "availability_time": join_multi_value(availability_time),
        "availability_notes": availability_notes,
        "is_admin": is_admin,
        "photo_bytes": photo_bytes,
        "photo_mime_type": photo_mime_type,
    }


def member_table_rows(members: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for member in members:
        rows.append(
            {
                "Nombre": display_name(member),
                "Apodo": member.get("nickname") or "-",
                "Edad": member.get("age") or "-",
                "Ubicacion": member.get("location") or "-",
                "Instagram": member.get("instagram") or "-",
                "Celular": member.get("phone") or "-",
                "Sistema de juego": member.get("gaming_system") or "-",
                "Actualmente jugando": member.get("currently_playing") or "-",
                "Foto": "Si" if member.get("has_photo") else "No",
                "Registro": format_date(member.get("created_at")),
            }
        )
    return pd.DataFrame(rows)


def birthday_rows_for_month(members: list[dict[str, Any]], month: int) -> pd.DataFrame:
    rows = []
    for member in members:
        parsed = parse_birthday_for_input(member.get("birthday"))
        if parsed is None or parsed.month != month:
            continue
        rows.append(
            {
                "Dia": parsed.day,
                "Nombre": display_name(member),
                "Apodo": member.get("nickname") or "-",
                "Cumpleanos": format_birthday_for_display(member.get("birthday")),
                "Instagram": member.get("instagram") or "-",
                "Sistema de juego": member.get("gaming_system") or "-",
            }
        )

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame(sorted(rows, key=lambda item: (item["Dia"], item["Nombre"])))


def birthday_calendar_rows(members: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for member in members:
        parsed = parse_birthday_for_input(member.get("birthday"))
        if parsed is None:
            continue
        rows.append(
            {
                "Mes": MONTH_NAMES_ES[parsed.month].capitalize(),
                "Dia": parsed.day,
                "Nombre": display_name(member),
                "Cumpleanos": format_birthday_for_display(member.get("birthday")),
            }
        )

    if not rows:
        return pd.DataFrame()

    month_order = {MONTH_NAMES_ES[index].capitalize(): index for index in MONTH_NAMES_ES}
    return pd.DataFrame(
        sorted(rows, key=lambda item: (month_order[item["Mes"]], item["Dia"], item["Nombre"]))
    )


def chunk_list(items: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def render_app_header(members: list[dict[str, Any]]) -> None:
    st.title(PAGE_TITLE)
    st.caption(
        "Registro de miembros, gustos, datos de contacto y perfil con foto. "
        f"Base activa: {get_database_backend()}."
    )

    nav = st.sidebar.radio(
        "Secciones",
        NAV_OPTIONS,
        index=NAV_OPTIONS.index(st.session_state["current_view"]),
    )
    st.sidebar.metric("Miembros registrados", len(members))
    st.sidebar.metric("Perfiles con foto", sum(1 for member in members if member.get("has_photo")))

    admin_members = [member for member in members if member.get("is_admin")]
    admin_pin = get_admin_pin()
    active_admin = get_active_admin_member(members)

    st.sidebar.markdown("### Permisos")
    if active_admin is not None:
        st.sidebar.success(f"Admin activo: {display_name(active_admin)}")
        if st.sidebar.button("Salir de modo admin", use_container_width=True):
            lock_admin_session()
            st.rerun()
    elif not admin_members:
        st.sidebar.info("No hay administradores marcados todavia.")
    elif not admin_pin:
        st.sidebar.warning("Configura `ADMIN_PIN` en Secrets para habilitar modo admin.")
    else:
        selected_admin_id = st.sidebar.selectbox(
            "Entrar como",
            options=[member["id"] for member in admin_members],
            format_func=lambda value: display_name(next(member for member in admin_members if member["id"] == value)),
        )
        entered_pin = st.sidebar.text_input("ADMIN_PIN", type="password")
        if st.sidebar.button("Entrar como admin", use_container_width=True):
            if entered_pin == admin_pin:
                st.session_state["admin_unlocked"] = True
                st.session_state["admin_session_member_id"] = selected_admin_id
                st.rerun()
            else:
                lock_admin_session()
                st.sidebar.error("PIN incorrecto.")

    st.sidebar.caption(
        "Si vas a publicar en Streamlit Cloud, configura DATABASE_URL para usar PostgreSQL."
    )

    if nav != st.session_state["current_view"]:
        st.session_state["current_view"] = nav
        st.rerun()


def render_summary(members: list[dict[str, Any]]) -> None:
    age_values = [member["age"] for member in members if member.get("age") is not None]
    average_age = round(sum(age_values) / len(age_values), 1) if age_values else "Sin dato"

    st.markdown(
        """
        <div style="padding:1rem 0 1.5rem 0;">
          <h2 class="gaymers-rainbow-title">B i e n v e n i d o s   a   G a y m e r s   G D L</h2>
          <p style="margin:.5rem 0 0 0; font-size:1.05rem;">
            Comunidad para conectar, cotorrear, jugar y ubicar rapido quien anda en linea,
            con que juega y cuando se arma la reta.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "Este espacio esta pensado primero para convivencia, retas, comunidad y buen cotorreo. "
        "Si de manera natural nacen amistades o algo mas entre personas del grupo, no hay bronca, "
        "pero la idea principal del grupo no es funcionar como espacio de ligue. "
        "La prioridad es mantener un ambiente claro, relajado y ordenado para todos."
    )

    banner_path = get_banner_path()
    if banner_path:
        st.image(banner_path, width="stretch")

    current_month = datetime.now().month
    st.markdown("### Cumpleanos del mes")
    birthday_columns = st.columns([1.2, 1.8])
    with birthday_columns[0]:
        birthday_banner = get_birthday_banner_path()
        if birthday_banner:
            st.image(birthday_banner, width="stretch")
    with birthday_columns[1]:
        current_month_birthdays = birthday_rows_for_month(members, current_month)
        if current_month_birthdays.empty:
            st.info(f"En {MONTH_NAMES_ES[current_month]} no hay cumpleaneros registrados todavia.")
        else:
            st.caption(f"Celebremos a quienes cumplen en {MONTH_NAMES_ES[current_month]}.")
            st.dataframe(current_month_birthdays, width="stretch", hide_index=True)

    metric_columns = st.columns(4)
    metric_columns[0].metric("Total de miembros", len(members))
    metric_columns[1].metric("Con foto", sum(1 for member in members if member.get("has_photo")))
    metric_columns[2].metric("Con Instagram", sum(1 for member in members if member.get("instagram")))
    metric_columns[3].metric("Edad promedio", average_age)

    if not members:
        st.info("Todavia no hay miembros registrados. Puedes empezar desde la seccion 'Nuevo miembro'.")
    else:
        st.markdown("### Ultimos registros")
        latest_members = sorted(
            members,
            key=lambda item: item.get("created_at") or 0,
            reverse=True,
        )[:5]
        latest_df = member_table_rows(latest_members)
        st.dataframe(latest_df, width="stretch", hide_index=True)

    admins = [member for member in members if member.get("is_admin")]
    st.markdown("### Administradores")
    if not admins:
        st.info("Todavia no hay administradores marcados.")
    else:
        for admin in admins:
            st.write(
                f"{display_name(admin)} | {value_or_fallback(admin.get('phone'))} | "
                f"{value_or_fallback(admin.get('instagram'))}"
            )


def render_new_member_page() -> None:
    st.subheader("Nuevo miembro")
    st.write("Captura aqui la informacion base del integrante y su foto.")

    with st.form("new_member_form", clear_on_submit=False):
        col_left, col_right = st.columns(2)

        with col_left:
            full_name = st.text_input("Nombre *")
            nickname = st.text_input("Apodo")
            age = st.selectbox("Edad", options=["", *[str(value) for value in range(10, 100)]])
            sexuality = st.selectbox("Sexualidad", options=SEXUALITY_OPTIONS)
            height_cm = st.selectbox("Altura en cm", options=["", *[str(value) for value in range(120, 231)]])
            location = st.text_input("Ubicacion")
            birthday_value = st.date_input(
                "Cumpleaños",
                value=None,
                min_value=BIRTHDAY_MIN_DATE,
                max_value=BIRTHDAY_MAX_DATE,
                format="DD/MM/YYYY",
            )
            instagram = st.text_input("Instagram", placeholder="@usuario")
            phone = st.text_input("Celular", placeholder="33...")
            zodiac_sign = calculate_zodiac_sign(birthday_value)
            st.text_input("Signo zodiacal", value=zodiac_sign or "", disabled=True)

        with col_right:
            favorite_color = st.text_input("Color favorito")
            favorite_food = st.text_input("Comida favorita")
            favorite_movies = st.text_input("Peliculas o genero favorito")
            music_tastes = st.multiselect("Gustos musicales", options=MUSIC_OPTIONS)
            music_tastes_other = st.text_input("Otros gustos musicales", placeholder="Opcional")
            hobbies = st.text_input("Ocio o deporte")
            favorite_character = st.text_input("Personaje favorito")
            gaming_system = st.multiselect("Sistema de juego", options=GAMING_SYSTEM_OPTIONS)
            gaming_system_other = st.text_input("Otro sistema de juego", placeholder="Opcional")
            currently_playing = st.text_input("Actualmente jugando")
            availability_days = st.multiselect("Dias disponibles para jugar", options=DAY_OPTIONS)
            availability_time = st.multiselect("Horario para jugar", options=TIME_OPTIONS)
            availability_notes = st.text_area("Notas de disponibilidad", placeholder="Ej. despues de las 9 pm")

        platform_ids = render_platform_id_inputs("new_member", {})

        uploaded_photo = st.file_uploader(
            "Foto de la persona",
            type=["png", "jpg", "jpeg", "webp"],
            help="La foto se guarda dentro de la base de datos.",
        )

        submitted = st.form_submit_button("Guardar miembro", width="stretch")

    if not submitted:
        return

    try:
        payload = build_member_payload(
            full_name=full_name,
            nickname=nickname,
            age=age,
            sexuality=sexuality,
            height_cm=height_cm,
            location=location,
            favorite_color=favorite_color,
            favorite_food=favorite_food,
            favorite_movies=favorite_movies,
            music_tastes=music_tastes,
            music_tastes_other=music_tastes_other,
            hobbies=hobbies,
            favorite_character=favorite_character,
            gaming_system=gaming_system,
            gaming_system_other=gaming_system_other,
            platform_ids=platform_ids,
            currently_playing=currently_playing,
            instagram=instagram,
            phone=phone,
            birthday_value=birthday_value,
            availability_days=availability_days,
            availability_time=availability_time,
            availability_notes=availability_notes,
            is_admin=False,
            uploaded_photo=uploaded_photo,
        )
        member = create_member(payload)
    except Exception as exc:
        st.error(str(exc))
        return

    set_flash("success", f"Se registro correctamente a {display_name(member)}.")
    st.session_state["selected_member_id"] = member["id"]
    st.session_state["pending_view"] = "Perfil"
    st.rerun()


def filter_members(
    members: list[dict[str, Any]],
    search_text: str,
    system_filter: str,
    photo_only: bool,
) -> list[dict[str, Any]]:
    normalized_search = search_text.strip().casefold()
    filtered_members: list[dict[str, Any]] = []

    for member in members:
        haystack = " ".join(
            value_or_fallback(member.get(field), "")
            for field in [
                "full_name",
                "nickname",
                "role",
                "location",
                "favorite_food",
                "favorite_movies",
                "music_tastes",
                "hobbies",
                "gaming_system",
                "platform_ids",
                "currently_playing",
                "phone",
                "availability_days",
                "availability_time",
                "availability_notes",
            ]
        ).casefold()

        if normalized_search and normalized_search not in haystack:
            continue

        member_systems = split_multi_value(member.get("gaming_system"))
        if system_filter != "Todos" and system_filter not in member_systems:
            continue

        if photo_only and not member.get("has_photo"):
            continue

        filtered_members.append(member)

    return filtered_members


def render_directory_page(members: list[dict[str, Any]]) -> None:
    st.subheader("Directorio")

    if not members:
        st.info("Aun no hay registros para mostrar.")
        return

    gaming_systems = sorted(
        {system for member in members for system in split_multi_value(member.get("gaming_system"))}
    )

    filter_columns = st.columns([2, 1, 1])
    search_text = filter_columns[0].text_input(
        "Buscar",
        placeholder="Nombre, apodo, ciudad, musica, consola...",
    )
    system_filter = filter_columns[1].selectbox(
        "Sistema",
        options=["Todos", *gaming_systems] if gaming_systems else ["Todos"],
    )
    photo_only = filter_columns[2].checkbox("Solo con foto")

    filtered_members = filter_members(members, search_text, system_filter, photo_only)

    st.caption(f"Resultados: {len(filtered_members)}")
    if not filtered_members:
        st.warning("No hubo coincidencias con esos filtros.")
        return

    directory_df = member_table_rows(filtered_members)
    st.dataframe(directory_df, width="stretch", hide_index=True)

    st.markdown("### Acceso rapido a perfiles")
    preview_members = filtered_members[:24]

    for group in chunk_list(preview_members, 3):
        columns = st.columns(len(group))
        for column, member in zip(columns, group):
            with column:
                with st.container(border=True):
                    if member.get("photo_bytes"):
                        st.image(member["photo_bytes"], width="stretch")
                    else:
                        st.info("Sin foto")

                    st.markdown(f"**{display_name(member)}**")
                    st.caption(value_or_fallback(member.get("location")))
                    st.write(f"Sistema: {value_or_fallback(member.get('gaming_system'))}")
                    st.write(f"Jugando: {value_or_fallback(member.get('currently_playing'))}")

                    if st.button("Ver perfil", key=f"open_profile_{member['id']}"):
                        open_member_profile(member["id"])

    if len(filtered_members) > len(preview_members):
        st.caption("La galeria rapida muestra los primeros 24 perfiles filtrados.")


def render_member_details(member: dict[str, Any]) -> None:
    photo_column, info_column = st.columns([1, 2])

    with photo_column:
        if member.get("photo_bytes"):
            st.image(member["photo_bytes"], width="stretch")
        else:
            st.info("Este perfil todavia no tiene foto.")

        st.caption(f"Alta: {format_date(member.get('created_at'))}")
        st.caption(f"Ultima actualizacion: {format_date(member.get('updated_at'))}")

    with info_column:
        render_member_profile_title(member)

        personal_columns = st.columns(2)
        with personal_columns[0]:
            render_rainbow_section_title("Datos personales")
            st.write(f"**Nombre:** {value_or_fallback(member.get('full_name'))}")
            st.write(f"**Apodo:** {value_or_fallback(member.get('nickname'))}")
            st.write(f"**Edad:** {value_or_fallback(member.get('age'))}")
            st.write(f"**Sexualidad:** {value_or_fallback(member.get('sexuality'))}")
            st.write(f"**Altura:** {value_or_fallback(member.get('height_cm'))}")
            st.write(f"**Ubicacion:** {value_or_fallback(member.get('location'))}")
            st.write(f"**Cumpleaños:** {format_birthday_for_display(member.get('birthday'))}")
            st.write(f"**Signo zodiacal:** {value_or_fallback(member.get('zodiac_sign'))}")

        with personal_columns[1]:
            render_rainbow_section_title("Gustos y hobbies")
            st.write(f"**Color favorito:** {value_or_fallback(member.get('favorite_color'))}")
            st.write(f"**Comida favorita:** {value_or_fallback(member.get('favorite_food'))}")
            st.write(f"**Peliculas:** {value_or_fallback(member.get('favorite_movies'))}")
            st.write(f"**Musica:** {value_or_fallback(member.get('music_tastes'))}")
            st.write(f"**Ocio o deporte:** {value_or_fallback(member.get('hobbies'))}")
            st.write(f"**Personaje favorito:** {value_or_fallback(member.get('favorite_character'))}")
            st.write(f"**Sistema de juego:** {value_or_fallback(member.get('gaming_system'))}")
            st.write(f"**Actualmente jugando:** {value_or_fallback(member.get('currently_playing'))}")

        render_rainbow_section_title("Juego online")
        platform_id_rows = parse_platform_ids_for_display(member.get("platform_ids"))
        if platform_id_rows:
            for system, player_id in platform_id_rows:
                st.write(f"**{platform_label(system)}:** {player_id}")
        else:
            st.write("**IDs por plataforma:** Sin dato")
        st.write(f"**Disponibilidad:** {format_availability(member)}")

        render_rainbow_section_title("Contacto")
        instagram_link = instagram_url(member.get("instagram"))
        if instagram_link:
            st.markdown(f"**Instagram:** [{member.get('instagram')}]({instagram_link})")
        else:
            st.write("**Instagram:** Sin dato")
        st.write(f"**Celular:** {value_or_fallback(member.get('phone'))}")


def render_edit_member_form(member: dict[str, Any]) -> None:
    with st.expander("Editar perfil", expanded=False):
        birthday_value = parse_birthday_for_input(member.get("birthday"))
        selected_music, custom_music = parse_existing_multiselect(member.get("music_tastes"), MUSIC_OPTIONS)
        selected_systems, custom_systems = parse_existing_multiselect(
            member.get("gaming_system"),
            GAMING_SYSTEM_OPTIONS,
        )
        selected_days, custom_days = parse_existing_multiselect(member.get("availability_days"), DAY_OPTIONS)
        selected_times, custom_times = parse_existing_multiselect(member.get("availability_time"), TIME_OPTIONS)
        existing_platform_ids = parse_json_map(member.get("platform_ids"))

        with st.form(f"edit_member_form_{member['id']}", clear_on_submit=False):
            col_left, col_right = st.columns(2)

            with col_left:
                full_name = st.text_input("Nombre *", value=member.get("full_name") or "")
                nickname = st.text_input("Apodo", value=member.get("nickname") or "")
                is_admin = st.checkbox("Es administrador", value=bool(member.get("is_admin")))
                age = st.selectbox(
                    "Edad",
                    options=["", *[str(value) for value in range(10, 100)]],
                    index=["", *[str(value) for value in range(10, 100)]].index(
                        str(member.get("age")) if member.get("age") is not None else ""
                    ),
                )
                sexuality = st.selectbox(
                    "Sexualidad",
                    options=SEXUALITY_OPTIONS,
                    index=SEXUALITY_OPTIONS.index(member.get("sexuality"))
                    if member.get("sexuality") in SEXUALITY_OPTIONS
                    else 0,
                )
                height_cm = st.selectbox(
                    "Altura en cm",
                    options=["", *[str(value) for value in range(120, 231)]],
                    index=["", *[str(value) for value in range(120, 231)]].index(
                        str(member.get("height_cm")) if member.get("height_cm") is not None else ""
                    ),
                )
                location = st.text_input("Ubicacion", value=member.get("location") or "")
                birthday_value = st.date_input(
                    "Cumpleaños",
                    value=birthday_value,
                    min_value=BIRTHDAY_MIN_DATE,
                    max_value=BIRTHDAY_MAX_DATE,
                    format="DD/MM/YYYY",
                )
                instagram = st.text_input("Instagram", value=member.get("instagram") or "")
                phone = st.text_input("Celular", value=member.get("phone") or "")
                zodiac_sign = calculate_zodiac_sign(birthday_value)
                st.text_input("Signo zodiacal", value=zodiac_sign or "", disabled=True)

            with col_right:
                favorite_color = st.text_input("Color favorito", value=member.get("favorite_color") or "")
                favorite_food = st.text_input("Comida favorita", value=member.get("favorite_food") or "")
                favorite_movies = st.text_input(
                    "Peliculas o genero favorito",
                    value=member.get("favorite_movies") or "",
                )
                music_tastes = st.multiselect(
                    "Gustos musicales",
                    options=MUSIC_OPTIONS,
                    default=selected_music,
                )
                music_tastes_other = st.text_input("Otros gustos musicales", value=custom_music)
                hobbies = st.text_input("Ocio o deporte", value=member.get("hobbies") or "")
                favorite_character = st.text_input(
                    "Personaje favorito",
                    value=member.get("favorite_character") or "",
                )
                gaming_system = st.multiselect(
                    "Sistema de juego",
                    options=GAMING_SYSTEM_OPTIONS,
                    default=selected_systems,
                )
                gaming_system_other = st.text_input("Otro sistema de juego", value=custom_systems)
                currently_playing = st.text_input(
                    "Actualmente jugando",
                    value=member.get("currently_playing") or "",
                )
                availability_days = st.multiselect(
                    "Dias disponibles para jugar",
                    options=DAY_OPTIONS,
                    default=selected_days,
                )
                availability_days_other = st.text_input("Otros dias o notas cortas", value=custom_days)
                availability_time = st.multiselect(
                    "Horario para jugar",
                    options=TIME_OPTIONS,
                    default=selected_times,
                )
                availability_time_other = st.text_input("Otros horarios", value=custom_times)
                availability_notes = st.text_area(
                    "Notas de disponibilidad",
                    value=member.get("availability_notes") or "",
                )

            platform_ids = render_platform_id_inputs(f"edit_member_{member['id']}", existing_platform_ids)

            uploaded_photo = st.file_uploader(
                "Reemplazar foto",
                type=["png", "jpg", "jpeg", "webp"],
                key=f"photo_replace_{member['id']}",
            )
            remove_photo = st.checkbox(
                "Eliminar foto actual",
                value=False,
                disabled=not member.get("has_photo"),
                key=f"remove_photo_{member['id']}",
            )

            submitted = st.form_submit_button("Guardar cambios", width="stretch")

        if not submitted:
            return

        try:
            payload = build_member_payload(
                full_name=full_name,
                nickname=nickname,
                age=age,
                sexuality=sexuality,
                role=member.get("role") or "",
                height_cm=height_cm,
                location=location,
                favorite_color=favorite_color,
                favorite_food=favorite_food,
                favorite_movies=favorite_movies,
                music_tastes=music_tastes,
                music_tastes_other=music_tastes_other,
                hobbies=hobbies,
                favorite_character=favorite_character,
                gaming_system=gaming_system,
                gaming_system_other=gaming_system_other,
                platform_ids=platform_ids,
                currently_playing=currently_playing,
                instagram=instagram,
                phone=phone,
                birthday_value=birthday_value,
                availability_days=availability_days + split_multi_value(availability_days_other),
                availability_time=availability_time + split_multi_value(availability_time_other),
                availability_notes=availability_notes,
                is_admin=is_admin,
                uploaded_photo=uploaded_photo,
                existing_member=member,
                remove_photo=remove_photo,
            )
            updated_member = update_member(member["id"], payload)
        except Exception as exc:
            st.error(str(exc))
            return

        if updated_member is None:
            st.error("No fue posible actualizar el perfil.")
            return

        set_flash("success", f"Se actualizaron los datos de {display_name(updated_member)}.")
        st.session_state["selected_member_id"] = updated_member["id"]
        st.rerun()


def render_delete_member(member: dict[str, Any], members: list[dict[str, Any]]) -> None:
    with st.expander("Eliminar registro", expanded=False):
        st.warning("Esta accion borra el perfil y su foto de forma permanente.")
        confirm = st.checkbox(
            "Confirmo que quiero eliminar este miembro.",
            key=f"confirm_delete_{member['id']}",
        )

        if st.button(
            "Eliminar miembro",
            disabled=not confirm,
            type="primary",
            key=f"delete_member_{member['id']}",
        ):
            deleted = delete_member(member["id"])
            if not deleted:
                st.error("No fue posible eliminar el registro.")
                return

            remaining_members = [item for item in members if item["id"] != member["id"]]
            st.session_state["selected_member_id"] = remaining_members[0]["id"] if remaining_members else None
            st.session_state["pending_view"] = "Directorio"
            set_flash("warning", f"Se elimino el perfil de {display_name(member)}.")
            st.rerun()


def render_profile_page(members: list[dict[str, Any]]) -> None:
    st.subheader("Perfil")

    if not members:
        st.info("No hay perfiles disponibles todavia.")
        return

    member_ids = [member["id"] for member in members]
    selected_id = st.session_state.get("selected_member_id")

    if selected_id not in member_ids:
        selected_id = member_ids[0]
        st.session_state["selected_member_id"] = selected_id

    selected_id = st.selectbox(
        "Selecciona un miembro",
        options=member_ids,
        index=member_ids.index(selected_id),
        format_func=lambda member_id: display_name(next(item for item in members if item["id"] == member_id)),
    )
    st.session_state["selected_member_id"] = selected_id

    member = get_member(selected_id)
    if member is None:
        st.error("No se encontro el perfil seleccionado.")
        return

    render_member_details(member)
    render_edit_member_form(member)
    if is_admin_session_active(members):
        render_delete_member(member, members)
    else:
        st.info("Solo un administrador puede editar o eliminar perfiles.")


def render_birthdays_page(members: list[dict[str, Any]]) -> None:
    st.subheader("Cumpleaños")

    birthday_banner = get_birthday_banner_path()
    if birthday_banner:
        st.image(birthday_banner, width="stretch")

    if not members:
        st.info("Todavia no hay miembros registrados.")
        return

    current_month = datetime.now().month
    current_month_birthdays = birthday_rows_for_month(members, current_month)

    st.markdown("### Cumpleañeros del mes")
    if current_month_birthdays.empty:
        st.info(f"En {MONTH_NAMES_ES[current_month]} no hay cumpleaneros registrados todavia.")
    else:
        st.dataframe(current_month_birthdays, width="stretch", hide_index=True)

    st.markdown("### Calendario anual")
    birthday_calendar = birthday_calendar_rows(members)
    if birthday_calendar.empty:
        st.info("Aun no hay fechas de cumpleanos registradas.")
    else:
        st.dataframe(birthday_calendar, width="stretch", hide_index=True)


def main() -> None:
    initialize_app()
    members = list_members()
    render_app_header(members)
    show_flash()

    current_view = st.session_state["current_view"]
    if current_view == "Resumen":
        render_summary(members)
    elif current_view == "Cumpleaños":
        render_birthdays_page(members)
    elif current_view == "Nuevo miembro":
        render_new_member_page()
    elif current_view == "Directorio":
        render_directory_page(members)
    else:
        render_profile_page(members)


if __name__ == "__main__":
    main()
