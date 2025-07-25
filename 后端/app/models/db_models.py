class UserToken:
    def __init__(self,token,user_id,expire_time):
        self.token=token
        self.user_id=user_id
        self.expire_time=expire_time

class User:
    def __init__(self,user_id,user_name,password,user_create_time,like_count=0,follower_count=0,following_count=0):
        self.user_id=user_id
        self.user_name=user_name
        self.password=password
        self.user_create_time=user_create_time
        self.like_count = like_count
        self.follower_count = follower_count
        self.following_count = following_count

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

class Like:
    def __init__(self, like_id, article_id, user_id, like_time):
        self.like_id = like_id
        self.article_id = article_id
        self.user_id = user_id
        self.like_time = like_time

class Follow:
    def __init__(self, follow_id, follower_id, followed_id, follow_time):
        self.follow_id = follow_id
        self.follower_id = follower_id
        self.followed_id = followed_id
        self.follow_time = follow_time