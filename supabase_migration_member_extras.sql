-- Migracion para una tabla public.members ya existente
-- Agrega campos nuevos para admins, role, celular, disponibilidad e IDs por plataforma

begin;

alter table public.members
    add column if not exists role varchar(50),
    add column if not exists platform_ids text,
    add column if not exists phone varchar(50),
    add column if not exists availability_days text,
    add column if not exists availability_time text,
    add column if not exists availability_notes text,
    add column if not exists is_admin boolean not null default false;

alter table public.members
    alter column gaming_system type text;

create index if not exists idx_members_role on public.members (role);
create index if not exists idx_members_is_admin on public.members (is_admin);
create index if not exists idx_members_phone on public.members (phone);

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

commit;
