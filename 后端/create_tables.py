from app.database import get_db

def create_tables():
    db = get_db()
    cursor = db.cursor()
    
    try:
        # 检查comments表是否存在
        cursor.execute("SHOW TABLES LIKE 'comments'")
        if not cursor.fetchone():
            print('创建comments表...')
            cursor.execute('''
                CREATE TABLE comments (
                    comments_id     int auto_increment primary key,
                    article_id      int not null,
                    user_id         int not null,
                    article_content text not null,
                    comment_time    datetime default CURRENT_TIMESTAMP null
                )
            ''')
            print('comments表创建成功!')
        else:
            print('comments表已存在')
            
        # 检查likes表是否存在
        cursor.execute("SHOW TABLES LIKE 'likes'")
        if not cursor.fetchone():
            print('创建likes表...')
            cursor.execute('''
                CREATE TABLE likes (
                    like_id    int auto_increment primary key,
                    article_id int not null,
                    user_id    int not null,
                    like_time  datetime default CURRENT_TIMESTAMP not null,
                    constraint article_id
                        foreign key (article_id) references publish (article_id),
                    constraint user_id
                        foreign key (user_id) references register (user_id)
                )
            ''')
            print('likes表创建成功!')
        else:
            print('likes表已存在')
            
        db.commit()
        print('表创建操作完成!')
    except Exception as e:
        db.rollback()
        print(f'创建表时出错: {str(e)}')
    finally:
        cursor.close()
        db.close()

if __name__ == '__main__':
    create_tables() 