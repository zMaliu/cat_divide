class User:
    def __init__(self,user_id,user_name,password,user_create_time):
        self.user_id=user_id
        self.user_name=user_name
        self.password=password
        self.user_create_time=user_create_time

class Post:
    def __init__(self,article_id,title,content,publish_time,user_id):
        self.article_id=article_id
        self.title=title
        self.content=content
        self.publish_time=publish_time
        self.user_id=user_id

class Comment:
    def __init__(self, comments_id, article_id, user_id, article_content, comment_time):
        self.comments_id = comments_id
        self.article_id = article_id
        self.user_id = user_id
        self.article_content = article_content
        self.comment_time = comment_time