-- Directorio Gaymers
-- SQL completo para PostgreSQL / Supabase
-- Ejecuta este archivo en el SQL Editor de Supabase.

begin;

create extension if not exists pgcrypto;
create extension if not exists pg_trgm;

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = timezone('utc', now());
    return new;
end;
$$;

create table if not exists public.members (
    id uuid primary key default gen_random_uuid(),
    full_name varchar(160) not null,
    nickname varchar(160),
    age integer,
    sexuality varchar(160),
    height_cm integer,
    location varchar(200),
    favorite_color varchar(120),
    favorite_food text,
    favorite_movies text,
    music_tastes text,
    hobbies text,
    zodiac_sign varchar(120),
    favorite_character text,
    gaming_system varchar(160),
    currently_playing text,
    instagram varchar(160),
    birthday varchar(120),
    photo_bytes bytea,
    photo_mime_type varchar(50),
    created_at timestamptz not null default timezone('utc', now()),
    updated_at timestamptz not null default timezone('utc', now()),
    constraint members_full_name_not_blank check (length(trim(full_name)) > 0),
    constraint members_age_non_negative check (age is null or age >= 0),
    constraint members_height_non_negative check (height_cm is null or height_cm >= 0),
    constraint members_photo_consistency check (
        (photo_bytes is null and photo_mime_type is null)
        or
        (photo_bytes is not null and photo_mime_type is not null)
    )
);

drop trigger if exists trg_members_updated_at on public.members;
create trigger trg_members_updated_at
before update on public.members
for each row
execute function public.set_updated_at();

create index if not exists idx_members_created_at
    on public.members (created_at desc);

create index if not exists idx_members_full_name
    on public.members (full_name);

create index if not exists idx_members_nickname
    on public.members (nickname);

create index if not exists idx_members_gaming_system
    on public.members (gaming_system);

create index if not exists idx_members_location
    on public.members (location);

create index if not exists idx_members_has_photo
    on public.members ((photo_bytes is not null));

create index if not exists idx_members_search_full_name_trgm
    on public.members using gin (full_name gin_trgm_ops);

create index if not exists idx_members_search_nickname_trgm
    on public.members using gin (nickname gin_trgm_ops);

create index if not exists idx_members_search_location_trgm
    on public.members using gin (location gin_trgm_ops);

create index if not exists idx_members_search_music_tastes_trgm
    on public.members using gin (music_tastes gin_trgm_ops);

create index if not exists idx_members_search_hobbies_trgm
    on public.members using gin (hobbies gin_trgm_ops);

create index if not exists idx_members_search_favorite_food_trgm
    on public.members using gin (favorite_food gin_trgm_ops);

create index if not exists idx_members_search_favorite_movies_trgm
    on public.members using gin (favorite_movies gin_trgm_ops);

create index if not exists idx_members_search_currently_playing_trgm
    on public.members using gin (currently_playing gin_trgm_ops);

create or replace view public.member_directory_view as
select
    id,
    full_name,
    nickname,
    age,
    sexuality,
    height_cm,
    location,
    favorite_color,
    favorite_food,
    favorite_movies,
    music_tastes,
    hobbies,
    zodiac_sign,
    favorite_character,
    gaming_system,
    currently_playing,
    instagram,
    birthday,
    (photo_bytes is not null) as has_photo,
    photo_mime_type,
    created_at,
    updated_at
from public.members;

comment on table public.members is
'Miembros del grupo Gaymers con datos personales, gustos, contacto y foto en la base de datos.';

comment on column public.members.photo_bytes is
'Foto binaria del miembro, almacenada como bytea.';

comment on column public.members.photo_mime_type is
'Tipo MIME de la foto, por ejemplo image/jpeg o image/png.';

comment on view public.member_directory_view is
'Vista ligera del directorio sin exponer el binario completo de la foto.';

commit;
