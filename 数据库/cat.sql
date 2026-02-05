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
    user_create_time datetime      not null on update CURRENT_TIMESTAMP
    user_avatar      varchar(255) default '/default.jpg' null comment '用户头像路径'
    user_bio         text null comment '个人简介',
    user_location    varchar(255) null comment '所在地',
    user_birthday    date null comment '生日'
)
    row_format = DYNAMIC;

create table cats
(
    cat_id      int auto_increment
        primary key,
    name        varchar(255)                                                  not null comment '猫咪名字',
    breed       varchar(255)                                                  null comment '品种',
    age         int                                                           null comment '年龄',
    gender      enum ('male', 'female', 'unknown') default 'unknown'          null comment '性别',
    description text                                                          null comment '描述',
    image_url   varchar(255)                       default '/default_cat.jpg' null comment '图片路径',
    owner_id    int                                                           not null comment '主人ID',
    status      int                                default 0                  not null comment '0:未审核 1:已通过 2:未通过',
    milvus_id   int                                                           null comment 'Milvus向量唯一ID（NULL表示未生成向量）',
    create_time datetime                           default CURRENT_TIMESTAMP  null,
    update_time datetime                           default CURRENT_TIMESTAMP  null on update CURRENT_TIMESTAMP,
    constraint cats_ibfk_1
        foreign key (owner_id) references register (user_id)
            on delete cascade
)
    row_format = DYNAMIC;

create index owner_id
    on cats (owner_id);

create table chat_sessions
(
    session_id   int auto_increment
        primary key,
    fromuser_id  int                                not null,
    touser_id    int                                not null,
    created_time datetime default CURRENT_TIMESTAMP null,
    updated_time datetime default CURRENT_TIMESTAMP null on update CURRENT_TIMESTAMP,
    constraint chat_sessions_ibfk_1
        foreign key (fromuser_id) references register (user_id),
    constraint chat_sessions_ibfk_2
        foreign key (touser_id) references register (user_id)
);

create index fromuser_id
    on chat_sessions (fromuser_id);

create index touser_id
    on chat_sessions (touser_id);

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

create table messages
(
    message_id   int auto_increment
        primary key,
    session_id   int                                  not null,
    fromuser_id  int                                  not null,
    touser_id    int                                  not null,
    content      text                                 not null,
    is_read      tinyint(1) default 0                 null,
    created_time datetime   default CURRENT_TIMESTAMP null,
    constraint messages_ibfk_1
        foreign key (session_id) references chat_sessions (session_id),
    constraint messages_ibfk_2
        foreign key (fromuser_id) references register (user_id),
    constraint messages_ibfk_3
        foreign key (touser_id) references register (user_id)
);

create index fromuser_id
    on messages (fromuser_id);

create index session_id
    on messages (session_id);

create index touser_id
    on messages (touser_id);

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

CREATE TABLE favorites
(
    favorite_id int auto_increment
        primary key,
    article_id  int                                not null comment '帖子ID',
    user_id     int                                not null comment '用户ID',
    favorite_time datetime default CURRENT_TIMESTAMP not null comment '收藏时间',
    constraint fk_favorites_article
        foreign key (article_id) references publish (article_id)
            on delete cascade,
    constraint fk_favorites_user
        foreign key (user_id) references register (user_id)
            on delete cascade,
    unique key uk_user_article (user_id, article_id) comment '用户和帖子的唯一索引，防止重复收藏'
) comment '用户收藏帖子表';

create definer = root@localhost view article_stats as
select `p`.`article_id` AS `article_id`, count(`l`.`like_id`) AS `like_count`
from (`cat`.`publish` `p` left join `cat`.`likes` `l` on ((`p`.`article_id` = `l`.`article_id`)))
group by `p`.`article_id`;

create definer = root@localhost view user_stats as
select `r`.`user_id`                       AS `user_id`,
       coalesce(`f1`.`follower_count`, 0)  AS `follower_count`,
       coalesce(`f2`.`following_count`, 0) AS `following_count`
from ((`cat`.`register` `r` left join (select `cat`.`follows`.`followed_id` AS `followed_id`,
                                              count(0)                      AS `follower_count`
                                       from `cat`.`follows`
                                       group by `cat`.`follows`.`followed_id`) `f1`
       on ((`r`.`user_id` = `f1`.`followed_id`))) left join (select `cat`.`follows`.`follower_id` AS `follower_id`,
                                                                    count(0)                      AS `following_count`
                                                             from `cat`.`follows`
                                                             group by `cat`.`follows`.`follower_id`) `f2`
      on ((`r`.`user_id` = `f2`.`follower_id`)));