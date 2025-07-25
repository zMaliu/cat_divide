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
    user_name        varchar(255)  not null,
    password         varchar(255)  not null,
    user_create_time datetime      not null on update CURRENT_TIMESTAMP,
    like_count       int default 0 null comment '获赞总数',
    follower_count   int default 0 null comment '粉丝数',
    following_count  int default 0 null comment '关注数'
)
    row_format = DYNAMIC;

create table follows
(
    follow_id   int auto_increment
        primary key,
    follower_id int                                not null comment '关注者ID',
    followed_id int                                not null comment '被关注者ID',
    follow_time datetime default CURRENT_TIMESTAMP null,
    constraint followed_id
        foreign key (followed_id) references register (user_id),
    constraint follower_id
        foreign key (follower_id) references register (user_id)
);

create table publish
(
    article_id   int auto_increment
        primary key,
    title        varchar(255)                        not null,
    content      text                                not null,
    img          varchar(255) default '/default.jpg' not null,
    publish_time datetime                            not null on update CURRENT_TIMESTAMP,
    user_id      int                                 not null,
    like_count   int          default 0              null comment '获赞总数',
    constraint fk_pubilsh_user
        foreign key (user_id) references register (user_id)
            on delete cascade
)
    row_format = DYNAMIC;

create table likes
(
    like_id    int auto_increment
        primary key,
    article_id int                                not null,
    user_id    int                                not null,
    like_time  datetime default CURRENT_TIMESTAMP not null,
    constraint article_id
        foreign key (article_id) references publish (article_id),
    constraint user_id
        foreign key (user_id) references register (user_id)
);


