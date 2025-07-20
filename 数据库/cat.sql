create table comments
(
    comments_id     int auto_increment
        primary key,
    article_id      int                                not null,
    user_id         int                                not null,
    article_content text                               not null,
    comment_time    datetime default CURRENT_TIMESTAMP null
);

create table register
(
    user_id          int auto_increment
        primary key,
    user_name        varchar(255) not null,
    password         varchar(255) not null,
    user_create_time datetime     not null on update CURRENT_TIMESTAMP
)
    row_format = DYNAMIC;

create table publish
(
    article_id   int auto_increment
        primary key,
    title        varchar(255)                        not null,
    content      text                                not null,
    img          varchar(255) default '/default.jpg' not null,
    publish_time datetime                            not null on update CURRENT_TIMESTAMP,
    user_id      int                                 not null,
    constraint fk_pubilsh_user
        foreign key (user_id) references register (user_id)
            on delete cascade
)
    row_format = DYNAMIC;


