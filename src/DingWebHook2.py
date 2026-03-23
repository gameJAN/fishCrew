from dingtalk_stream import AckMessage, ChatbotMessage, DingTalkStreamClient, Credential,ChatbotHandler,CallbackMessage
from src.Agents import AgentClass
from src.Storage import add_user
from dotenv import load_dotenv as _load_dotenv
_load_dotenv()
import os 
import logging

def setup_logging():
    """设置日志配置"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("dingtalk_connection.log",encoding='utf-8')
        ]
    )
    return logging.getLogger("DingTalk")

user_storage = {}

class EchoTextHandler(ChatbotHandler):
    """钉钉机器人消息处理器，用于接受和相应钉钉聊天消息"""
    def __init__(self):
        super(ChatbotHandler,self).__init__()

    async def process(self,callback:CallbackMessage):
        """处理消息的主要方法 
        Args:
            callback: 钉钉回调消息对象
        Retruns:
            元组: 状态码和状态消息
        """
        logger = setup_logging()
        # 从回调数据中提取聊天消息
        incoming_message = ChatbotMessage.from_dict(callback.data)

        logger.info(incoming_message)
        logger.info(callback.data)

        # 提取消息文本内容去除前后空白
        text = incoming_message.text.content.strip()
        # 获取发送者的用户ID
        userid = callback.data["senderStaffId"]

        add_user("userid",userid)

        # 使用AI代理处理用户消息
        msg = AgentClass().run_agent(text)
        logger.info(msg)

        # 回复处理后的消息
        self.reply_text(msg["output"], incoming_message)

        return AckMessage.STATUS_OK, "ok"
    
def main():
    logger = setup_logging()
    logger.info("启动钉钉流客户端")

    logger.info(f"应用ID：{os.getenv('DINGDING_ID')}")
    logger.info("使用凭证链接钉钉")

    try:
        # DingTalkStreamClient这个主要是建立websocket链接
        credential = Credential(os.getenv("DINGDING_ID"),os.getenv("DINGDING_SECRET"))
        client = DingTalkStreamClient(credential,logger=logger)
        logger.info("钉钉客户端创建成功")

        # 注册回调处理器 处理websocket返回的数据
        client.register_callback_handler(ChatbotMessage.TOPIC,EchoTextHandler())
        logger.info("已注册ChatbtMessage的回调处理")

        # 启动客户端
        logger.info("正在启动钉钉客户端..")
        client.start_forever()
    except Exception as e:
        logger.error(f"链接钉钉时出错:{e}",exc_info=True) 

if __name__  == "__main__":
    main()

