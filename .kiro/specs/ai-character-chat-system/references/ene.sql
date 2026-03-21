create type action_type as enum ('AI', 'PERSON');

alter type action_type owner to ene;

create table if not exists person
(
    id         serial
        primary key,
    name       text                    not null,
    created_at timestamp default now() not null,
    updated_at timestamp default now() not null,
    profile    text
);

alter table person
    owner to ene;

create table if not exists reflection
(
    id         serial
        primary key,
    parent_id  integer,
    summary    text                    not null,
    created_at timestamp default now() not null
);

alter table reflection
    owner to ene;

create table if not exists message
(
    id            serial
        primary key,
    person_id     integer
        references person,
    content       text                    not null,
    action        action_type             not null,
    created_at    timestamp default now() not null,
    reflection_id integer
        references reflection
);

alter table message
    owner to ene;

create table if not exists last_reflected_id
(
    id         integer not null
        primary key
        references person,
    message_id integer
);

alter table last_reflected_id
    owner to ene;

create table if not exists episode
(
    id         serial
        primary key,
    title      text                not null,
    summary    text                not null,
    important  integer   default 1 not null,
    created_at timestamp default now()
);

alter table episode
    owner to ene;

create table if not exists tag
(
    id         serial
        primary key,
    tag        text not null,
    created_at timestamp default now()
);

alter table tag
    owner to ene;

create table if not exists tag_message
(
    id         serial
        primary key,
    tag_id     integer not null
        references tag,
    message_id integer not null
        references message
);

alter table tag_message
    owner to ene;

create table if not exists tag_reflection
(
    id            serial
        primary key,
    tag_id        integer not null
        references tag,
    reflection_id integer not null
        references reflection
);

alter table tag_reflection
    owner to ene;

create table if not exists tag_episode
(
    id         serial
        primary key,
    tag_id     integer not null
        references tag,
    episode_id integer not null
        references episode
);

alter table tag_episode
    owner to ene;

