from __future__ import annotations

from io import BytesIO
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

PAGE_TITLE = "Directorio Gaymers"
NAV_OPTIONS = ["Resumen", "Nuevo miembro", "Directorio", "Perfil"]


def initialize_app() -> None:
    st.set_page_config(page_title=PAGE_TITLE, layout="wide")
    init_db()

    if "current_view" not in st.session_state:
        st.session_state["current_view"] = "Resumen"

    if "selected_member_id" not in st.session_state:
        st.session_state["selected_member_id"] = None

    if "flash_message" not in st.session_state:
        st.session_state["flash_message"] = None


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
        return f"{nickname} ({member['full_name']})"
    return member["full_name"]


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
    st.session_state["current_view"] = "Perfil"
    st.rerun()


def build_member_payload(
    *,
    full_name: str,
    nickname: str,
    age: str,
    sexuality: str,
    height_cm: str,
    location: str,
    favorite_color: str,
    favorite_food: str,
    favorite_movies: str,
    music_tastes: str,
    hobbies: str,
    zodiac_sign: str,
    favorite_character: str,
    gaming_system: str,
    currently_playing: str,
    instagram: str,
    birthday: str,
    uploaded_photo,
    existing_member: dict[str, Any] | None = None,
    remove_photo: bool = False,
) -> dict[str, Any]:
    clean_name = full_name.strip()
    if not clean_name:
        raise ValueError("El nombre es obligatorio.")

    photo_bytes = existing_member.get("photo_bytes") if existing_member else None
    photo_mime_type = existing_member.get("photo_mime_type") if existing_member else None

    if remove_photo:
        photo_bytes = None
        photo_mime_type = None

    if uploaded_photo is not None:
        photo_bytes, photo_mime_type = process_uploaded_photo(uploaded_photo)

    return {
        "full_name": clean_name,
        "nickname": nickname,
        "age": parse_optional_int(age, "La edad"),
        "sexuality": sexuality,
        "height_cm": parse_optional_int(height_cm, "La altura"),
        "location": location,
        "favorite_color": favorite_color,
        "favorite_food": favorite_food,
        "favorite_movies": favorite_movies,
        "music_tastes": music_tastes,
        "hobbies": hobbies,
        "zodiac_sign": zodiac_sign,
        "favorite_character": favorite_character,
        "gaming_system": gaming_system,
        "currently_playing": currently_playing,
        "instagram": instagram,
        "birthday": birthday,
        "photo_bytes": photo_bytes,
        "photo_mime_type": photo_mime_type,
    }


def member_table_rows(members: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for member in members:
        rows.append(
            {
                "Nombre": member["full_name"],
                "Apodo": member.get("nickname") or "-",
                "Edad": member.get("age") or "-",
                "Ubicacion": member.get("location") or "-",
                "Instagram": member.get("instagram") or "-",
                "Sistema de juego": member.get("gaming_system") or "-",
                "Actualmente jugando": member.get("currently_playing") or "-",
                "Foto": "Si" if member.get("has_photo") else "No",
                "Registro": format_date(member.get("created_at")),
            }
        )
    return pd.DataFrame(rows)


def chunk_list(items: list[dict[str, Any]], size: int) -> list[list[dict[str, Any]]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def render_app_header(members: list[dict[str, Any]]) -> None:
    st.title(PAGE_TITLE)
    st.caption(
        "Registro de miembros, gustos, datos de contacto y perfil con foto. "
        f"Base activa: {get_database_backend()}."
    )

    nav = st.sidebar.radio("Secciones", NAV_OPTIONS, key="current_view")
    st.sidebar.metric("Miembros registrados", len(members))
    st.sidebar.metric("Perfiles con foto", sum(1 for member in members if member.get("has_photo")))
    st.sidebar.caption(
        "Si vas a publicar en Streamlit Cloud, configura DATABASE_URL para usar PostgreSQL."
    )

    if nav != st.session_state["current_view"]:
        st.session_state["current_view"] = nav


def render_summary(members: list[dict[str, Any]]) -> None:
    st.subheader("Resumen general")

    age_values = [member["age"] for member in members if member.get("age") is not None]
    average_age = round(sum(age_values) / len(age_values), 1) if age_values else "Sin dato"

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
        st.dataframe(latest_df, use_container_width=True, hide_index=True)

    st.markdown("### Formato base del grupo")
    st.code(
        "\n".join(
            [
                "Nombre:",
                "Edad:",
                "Sexualidad:",
                "Altura:",
                "Ubicacion:",
                "Color favorito:",
                "Comida favorita:",
                "Peliculas:",
                "Gustos musicales:",
                "Ocio o deporte:",
                "Signo zodiacal:",
                "Personaje favorito:",
                "Sistema de juego:",
                "Actualmente jugando:",
                "Instagram:",
                "Cumpleanos:",
                "Nombre o apodo:",
            ]
        ),
        language="text",
    )


def render_new_member_page() -> None:
    st.subheader("Nuevo miembro")
    st.write("Captura aqui la informacion base del integrante y su foto.")

    with st.form("new_member_form", clear_on_submit=False):
        col_left, col_right = st.columns(2)

        with col_left:
            full_name = st.text_input("Nombre *")
            nickname = st.text_input("Apodo")
            age = st.text_input("Edad", placeholder="Ej. 36")
            sexuality = st.text_input("Sexualidad")
            height_cm = st.text_input("Altura en cm", placeholder="Ej. 172")
            location = st.text_input("Ubicacion")
            birthday = st.text_input("Cumpleanos", placeholder="Ej. 26 de febrero")
            instagram = st.text_input("Instagram", placeholder="@usuario")

        with col_right:
            favorite_color = st.text_input("Color favorito")
            favorite_food = st.text_input("Comida favorita")
            favorite_movies = st.text_input("Peliculas o genero favorito")
            music_tastes = st.text_input("Gustos musicales")
            hobbies = st.text_input("Ocio o deporte")
            zodiac_sign = st.text_input("Signo zodiacal")
            favorite_character = st.text_input("Personaje favorito")
            gaming_system = st.text_input("Sistema de juego")
            currently_playing = st.text_input("Actualmente jugando")

        uploaded_photo = st.file_uploader(
            "Foto del miembro",
            type=["png", "jpg", "jpeg", "webp"],
            help="La foto se guarda dentro de la base de datos.",
        )

        submitted = st.form_submit_button("Guardar miembro", use_container_width=True)

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
            hobbies=hobbies,
            zodiac_sign=zodiac_sign,
            favorite_character=favorite_character,
            gaming_system=gaming_system,
            currently_playing=currently_playing,
            instagram=instagram,
            birthday=birthday,
            uploaded_photo=uploaded_photo,
        )
        member = create_member(payload)
    except Exception as exc:
        st.error(str(exc))
        return

    set_flash("success", f"Se registro correctamente a {display_name(member)}.")
    st.session_state["selected_member_id"] = member["id"]
    st.session_state["current_view"] = "Perfil"
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
                "location",
                "favorite_food",
                "favorite_movies",
                "music_tastes",
                "hobbies",
                "gaming_system",
                "currently_playing",
            ]
        ).casefold()

        if normalized_search and normalized_search not in haystack:
            continue

        if system_filter != "Todos" and (member.get("gaming_system") or "Sin dato") != system_filter:
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
        {
            member.get("gaming_system") or "Sin dato"
            for member in members
        }
    )

    filter_columns = st.columns([2, 1, 1])
    search_text = filter_columns[0].text_input(
        "Buscar",
        placeholder="Nombre, apodo, ciudad, musica, consola...",
    )
    system_filter = filter_columns[1].selectbox(
        "Sistema",
        options=["Todos", *gaming_systems],
    )
    photo_only = filter_columns[2].checkbox("Solo con foto")

    filtered_members = filter_members(members, search_text, system_filter, photo_only)

    st.caption(f"Resultados: {len(filtered_members)}")
    if not filtered_members:
        st.warning("No hubo coincidencias con esos filtros.")
        return

    directory_df = member_table_rows(filtered_members)
    st.dataframe(directory_df, use_container_width=True, hide_index=True)

    st.markdown("### Acceso rapido a perfiles")
    preview_members = filtered_members[:24]

    for group in chunk_list(preview_members, 3):
        columns = st.columns(len(group))
        for column, member in zip(columns, group):
            with column:
                with st.container(border=True):
                    if member.get("photo_bytes"):
                        st.image(member["photo_bytes"], use_container_width=True)
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
            st.image(member["photo_bytes"], use_container_width=True)
        else:
            st.info("Este perfil todavia no tiene foto.")

        st.caption(f"Alta: {format_date(member.get('created_at'))}")
        st.caption(f"Ultima actualizacion: {format_date(member.get('updated_at'))}")

    with info_column:
        st.subheader(display_name(member))

        personal_columns = st.columns(2)
        with personal_columns[0]:
            st.markdown("### Datos personales")
            st.write(f"**Nombre:** {value_or_fallback(member.get('full_name'))}")
            st.write(f"**Apodo:** {value_or_fallback(member.get('nickname'))}")
            st.write(f"**Edad:** {value_or_fallback(member.get('age'))}")
            st.write(f"**Sexualidad:** {value_or_fallback(member.get('sexuality'))}")
            st.write(f"**Altura:** {value_or_fallback(member.get('height_cm'))}")
            st.write(f"**Ubicacion:** {value_or_fallback(member.get('location'))}")
            st.write(f"**Cumpleanos:** {value_or_fallback(member.get('birthday'))}")
            st.write(f"**Signo zodiacal:** {value_or_fallback(member.get('zodiac_sign'))}")

        with personal_columns[1]:
            st.markdown("### Gustos y hobbies")
            st.write(f"**Color favorito:** {value_or_fallback(member.get('favorite_color'))}")
            st.write(f"**Comida favorita:** {value_or_fallback(member.get('favorite_food'))}")
            st.write(f"**Peliculas:** {value_or_fallback(member.get('favorite_movies'))}")
            st.write(f"**Musica:** {value_or_fallback(member.get('music_tastes'))}")
            st.write(f"**Ocio o deporte:** {value_or_fallback(member.get('hobbies'))}")
            st.write(f"**Personaje favorito:** {value_or_fallback(member.get('favorite_character'))}")
            st.write(f"**Sistema de juego:** {value_or_fallback(member.get('gaming_system'))}")
            st.write(f"**Actualmente jugando:** {value_or_fallback(member.get('currently_playing'))}")

        st.markdown("### Contacto")
        instagram_link = instagram_url(member.get("instagram"))
        if instagram_link:
            st.markdown(f"**Instagram:** [{member.get('instagram')}]({instagram_link})")
        else:
            st.write("**Instagram:** Sin dato")


def render_edit_member_form(member: dict[str, Any]) -> None:
    with st.expander("Editar perfil", expanded=False):
        with st.form(f"edit_member_form_{member['id']}", clear_on_submit=False):
            col_left, col_right = st.columns(2)

            with col_left:
                full_name = st.text_input("Nombre *", value=member.get("full_name") or "")
                nickname = st.text_input("Apodo", value=member.get("nickname") or "")
                age = st.text_input("Edad", value=value_or_fallback(member.get("age"), ""))
                sexuality = st.text_input("Sexualidad", value=member.get("sexuality") or "")
                height_cm = st.text_input("Altura en cm", value=value_or_fallback(member.get("height_cm"), ""))
                location = st.text_input("Ubicacion", value=member.get("location") or "")
                birthday = st.text_input("Cumpleanos", value=member.get("birthday") or "")
                instagram = st.text_input("Instagram", value=member.get("instagram") or "")

            with col_right:
                favorite_color = st.text_input("Color favorito", value=member.get("favorite_color") or "")
                favorite_food = st.text_input("Comida favorita", value=member.get("favorite_food") or "")
                favorite_movies = st.text_input(
                    "Peliculas o genero favorito",
                    value=member.get("favorite_movies") or "",
                )
                music_tastes = st.text_input("Gustos musicales", value=member.get("music_tastes") or "")
                hobbies = st.text_input("Ocio o deporte", value=member.get("hobbies") or "")
                zodiac_sign = st.text_input("Signo zodiacal", value=member.get("zodiac_sign") or "")
                favorite_character = st.text_input(
                    "Personaje favorito",
                    value=member.get("favorite_character") or "",
                )
                gaming_system = st.text_input("Sistema de juego", value=member.get("gaming_system") or "")
                currently_playing = st.text_input(
                    "Actualmente jugando",
                    value=member.get("currently_playing") or "",
                )

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

            submitted = st.form_submit_button("Guardar cambios", use_container_width=True)

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
                hobbies=hobbies,
                zodiac_sign=zodiac_sign,
                favorite_character=favorite_character,
                gaming_system=gaming_system,
                currently_playing=currently_playing,
                instagram=instagram,
                birthday=birthday,
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
            st.session_state["current_view"] = "Directorio"
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
    render_delete_member(member, members)


def main() -> None:
    initialize_app()
    members = list_members()
    render_app_header(members)
    show_flash()

    current_view = st.session_state["current_view"]
    if current_view == "Resumen":
        render_summary(members)
    elif current_view == "Nuevo miembro":
        render_new_member_page()
    elif current_view == "Directorio":
        render_directory_page(members)
    else:
        render_profile_page(members)


if __name__ == "__main__":
    main()
