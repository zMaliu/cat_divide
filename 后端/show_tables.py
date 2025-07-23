from app.database import get_db
import pymysql

def show_tables():
    print("正在连接数据库...")
    try:
        db = get_db()
        cursor = db.cursor()
        
        print("数据库连接成功!")
        try:
            print("执行 SHOW TABLES 查询")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print("\n现有数据库表:")
            if not tables:
                print("数据库中没有表")
            else:
                for table in tables:
                    table_name = table[0] if isinstance(table, tuple) else table['Tables_in_cat']
                    print(f"- {table_name}")
                
            # 检查likes和comments表的行数
            print("\n检查特定表:")
            for table_name in ['likes', 'comments', 'register', 'publish']:
                try:
                    print(f"检查表 '{table_name}'...")
                    cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
                    if cursor.fetchone():
                        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        count = cursor.fetchone()[0]
                        print(f"  {table_name}表存在，包含 {count} 条记录")
                    else:
                        print(f"  {table_name}表不存在")
                except Exception as e:
                    print(f"  查询{table_name}表失败: {str(e)}")
                    
        except Exception as e:
            print(f"查询表结构失败: {str(e)}")
        finally:
            cursor.close()
            db.close()
            print("\n数据库连接已关闭")
    except Exception as e:
        print(f"连接数据库失败: {str(e)}")

if __name__ == '__main__':
    print("开始执行脚本...")
    show_tables()
    print("脚本执行完成") 