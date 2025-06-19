import schedule
import time
import logging
from datetime import datetime
import sys
import os

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scheduler.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

def run_data_request():
    try:
        logging.info("开始执行数据请求任务")
        # 获取当前脚本所在目录
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 切换到脚本所在目录
        os.chdir(current_dir)
        # 执行Data_request.py
        exec(open('Data_request.py', encoding='utf-8').read())
        logging.info("数据请求任务执行完成")
    except Exception as e:
        logging.error(f"执行任务时发生错误: {str(e)}")

def main():
    logging.info("调度器启动")
    
    # 设置每天执行一次
    schedule.every().day.at("00:00").do(run_data_request)
    
    # 立即执行一次（可选）
    # run_data_request()
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次是否有待执行的任务
        except Exception as e:
            logging.error(f"调度器运行错误: {str(e)}")
            time.sleep(300)  # 发生错误时等待5分钟后继续

if __name__ == "__main__":
    main() 