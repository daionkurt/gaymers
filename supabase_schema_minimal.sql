-- Version minima y segura para Supabase
-- Crea la tabla principal sin depender de extensiones extra

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
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    constraint members_full_name_not_blank check (length(trim(full_name)) > 0),
    constraint members_age_non_negative check (age is null or age >= 0),
    constraint members_height_non_negative check (height_cm is null or height_cm >= 0)
);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists trg_members_updated_at on public.members;
create trigger trg_members_updated_at
before update on public.members
for each row
execute function public.set_updated_at();

create index if not exists idx_members_created_at on public.members (created_at desc);
create index if not exists idx_members_full_name on public.members (full_name);
create index if not exists idx_members_gaming_system on public.members (gaming_system);
create index if not exists idx_members_location on public.members (location);
