-- Directorio Gaymers
-- SQL completo para PostgreSQL / Supabase
-- Ejecuta este archivo en instalaciones nuevas.

begin;

create extension if not exists pgcrypto;

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
    role varchar(50),
    height_cm integer,
    location varchar(200),
    favorite_color varchar(120),
    favorite_food text,
    favorite_movies text,
    music_tastes text,
    hobbies text,
    zodiac_sign varchar(120),
    favorite_character text,
    gaming_system text,
    platform_ids text,
    currently_playing text,
    instagram varchar(160),
    phone varchar(50),
    birthday varchar(120),
    availability_days text,
    availability_time text,
    availability_notes text,
    is_admin boolean not null default false,
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

create index if not exists idx_members_created_at on public.members (created_at desc);
create index if not exists idx_members_full_name on public.members (full_name);
create index if not exists idx_members_nickname on public.members (nickname);
create index if not exists idx_members_role on public.members (role);
create index if not exists idx_members_location on public.members (location);
create index if not exists idx_members_is_admin on public.members (is_admin);

create or replace view public.member_directory_view as
select
    id,
    full_name,
    nickname,
    age,
    sexuality,
    role,
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
    platform_ids,
    currently_playing,
    instagram,
    phone,
    birthday,
    availability_days,
    availability_time,
    availability_notes,
    is_admin,
    (photo_bytes is not null) as has_photo,
    photo_mime_type,
    created_at,
    updated_at
from public.members;

comment on table public.members is
'Miembros del grupo Gaymers con datos personales, gustos, contacto, disponibilidad y foto.';

commit;
