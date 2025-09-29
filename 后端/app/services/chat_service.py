from app.database import get_db
from app.schemas.response import BaseResponse
import pymysql


def format_datetime(dt):
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')

class ChatService:
    @staticmethod
    def create_or_get_session(fromuser_id, touser_id):
        """
        创建或获取聊天会话
        """
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            # 检查是否已存在会话（双向检查）
            cursor.execute("""
                SELECT cs.*, r.user_name as target_user_name
                FROM chat_sessions cs
                JOIN register r ON r.user_id = %s
                WHERE (cs.fromuser_id = %s AND cs.touser_id = %s) OR (cs.fromuser_id = %s AND cs.touser_id = %s)
            """, (touser_id, fromuser_id, touser_id, touser_id, fromuser_id))

            session = cursor.fetchone()

            if not session:
                # 创建新会话
                cursor.execute("""
                    INSERT INTO chat_sessions (fromuser_id, touser_id)
                    VALUES (%s, %s)
                """, (fromuser_id, touser_id))
                db.commit()

                # 获取新创建的会话和目标用户信息
                cursor.execute("""
                    SELECT cs.*, r.user_name as target_user_name
                    FROM chat_sessions cs
                    JOIN register r ON r.user_id = %s
                    WHERE cs.session_id = %s
                """, (touser_id, cursor.lastrowid))
                session = cursor.fetchone()

            return BaseResponse.success({"session": session})
        except Exception as e:
            db.rollback()
            return BaseResponse.error(500, f"创建/获取会话失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def send_message(session_id, fromuser_id, content):
        """
        发送消息
        """
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            # 获取会话信息以确定接收者
            cursor.execute("""
                SELECT fromuser_id, touser_id FROM chat_sessions 
                WHERE session_id = %s
            """, (session_id,))

            session = cursor.fetchone()
            if not session:
                return BaseResponse.error(404, "会话不存在")

            # 确定接收者ID
            if session['fromuser_id'] == fromuser_id:
                touser_id = session['touser_id']
            elif session['touser_id'] == fromuser_id:
                touser_id = session['fromuser_id']
            else:
                return BaseResponse.error(403, "无权限在此会话中发送消息")

            # 插入消息
            cursor.execute("""
                INSERT INTO messages (session_id, fromuser_id, touser_id, content)
                VALUES (%s, %s, %s, %s)
            """, (session_id, fromuser_id, touser_id, content))

            db.commit()

            # 更新会话更新时间
            cursor.execute("""
                UPDATE chat_sessions SET updated_time = NOW() 
                WHERE session_id = %s
            """, (session_id,))
            db.commit()

            # 获取插入的消息
            cursor.execute("""
                SELECT * FROM messages WHERE message_id = %s
            """, (cursor.lastrowid,))
            message = cursor.fetchone()

            return BaseResponse.success({"message": message})
        except Exception as e:
            db.rollback()
            return BaseResponse.error(500, f"发送消息失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def get_sessions(user_id, page=1, per_page=10):
        """
        获取用户的会话列表
        """
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            offset = (page - 1) * per_page
            cursor.execute("""
                SELECT 
                    cs.*,
                    CASE 
                        WHEN cs.fromuser_id = %s THEN r2.user_name
                        ELSE r1.user_name
                    END as other_user_name,
                    (SELECT COUNT(*) FROM messages m 
                     WHERE m.session_id = cs.session_id 
                     AND m.touser_id = %s 
                     AND m.is_read = FALSE) as unread_count,
                    (SELECT content FROM messages m 
                     WHERE m.session_id = cs.session_id 
                     ORDER BY m.created_time DESC 
                     LIMIT 1) as last_message
                FROM chat_sessions cs
                JOIN register r1 ON cs.fromuser_id = r1.user_id
                JOIN register r2 ON cs.touser_id = r2.user_id
                WHERE cs.fromuser_id = %s OR cs.touser_id = %s
                ORDER BY cs.updated_time DESC
                LIMIT %s OFFSET %s
            """, (user_id, user_id, user_id, user_id, per_page, offset))

            sessions = cursor.fetchall()
            print(f"查询到的会话数据类型: {type(sessions)}")
            print(f"会话数据内容: {sessions}")
            
            # 确保sessions是列表类型
            if sessions is None:
                sessions = []
            
            for session in sessions:
                if 'updated_time' in session and session['updated_time']:
                    session['updated_time'] = format_datetime(session['updated_time'])
                if 'created_time' in session and session['created_time']:
                    session['created_time'] = format_datetime(session['created_time'])
            
            print(f"处理后的会话数据: {sessions}")
            return BaseResponse.success({"sessions": sessions})

        except Exception as e:
            return BaseResponse.error(500, f"获取会话列表失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def get_messages(session_id, user_id, page=1, per_page=20):
        """
        获取会话中的消息
        """
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            # 验证用户是否有权限访问此会话
            cursor.execute("""
                SELECT * FROM chat_sessions 
                WHERE session_id = %s AND (fromuser_id = %s OR touser_id = %s)
            """, (session_id, user_id, user_id))

            session = cursor.fetchone()
            if not session:
                return BaseResponse.error(403, "无权限访问此会话")

            offset = (page - 1) * per_page
            cursor.execute("""
                SELECT m.*, r.user_name as sender_name
                FROM messages m
                JOIN register r ON m.fromuser_id = r.user_id
                WHERE m.session_id = %s
                ORDER BY m.created_time DESC
                LIMIT %s OFFSET %s
            """, (session_id, per_page, offset))

            messages = cursor.fetchall()
            
            # 获取目标用户信息
            if messages:
                # 确定目标用户ID
                if session['fromuser_id'] == user_id:
                    target_user_id = session['touser_id']
                else:
                    target_user_id = session['fromuser_id']
                
                # 获取目标用户名
                cursor.execute("""
                    SELECT user_name FROM register WHERE user_id = %s
                """, (target_user_id,))
                target_user = cursor.fetchone()
                target_user_name = target_user['user_name'] if target_user else '用户'
                
                # 将目标用户名添加到每条消息中
                for message in messages:
                    message['target_user_name'] = target_user_name
            for message in messages:
                if 'created_time' in message:
                    message['created_time'] = format_datetime(message['created_time'])

            # 将消息标记为已读
            cursor.execute("""
                UPDATE messages 
                SET is_read = TRUE 
                WHERE session_id = %s AND touser_id = %s AND is_read = FALSE
            """, (session_id, user_id))
            db.commit()

            # 反转消息顺序，使最新的消息在最后
            messages.reverse()

            return BaseResponse.success({"messages": messages})
        except Exception as e:
            return BaseResponse.error(500, f"获取消息失败: {str(e)}")
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def get_unread_count(user_id):
        """
        获取未读消息数
        """
        db = get_db()
        cursor = db.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute("""
                SELECT COUNT(*) as unread_count
                FROM messages 
                WHERE touser_id = %s AND is_read = FALSE
            """, (user_id,))

            result = cursor.fetchone()
            return BaseResponse.success({"unread_count": result['unread_count']})
        except Exception as e:
            return BaseResponse.error(500, f"获取未读消息数失败: {str(e)}")
        finally:
            cursor.close()
            db.close()
