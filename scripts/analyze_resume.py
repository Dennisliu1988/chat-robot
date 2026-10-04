# scripts/analyze_resume.py
"""
学习测试脚本：简历分析与结构化提取测试
演示了 Prompt 约束、少样本、CoT 思维链、负面约束、流式输出与 Pydantic 校验重试等技巧。
"""
import os
import asyncio
import json
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv()


# ========== Pydantic 模型定义 ==========
class SkillAnalysis(BaseModel):
    """简历技能分析结果"""
    skills: list[str]                    # 技能列表
    years_of_experience: int             # 工作年限
    seniority: str                       # 资历等级: junior / mid / senior

class JobMatchResult(BaseModel):
    """职位匹配结果"""
    match_score: int                     # 匹配分数 (0-100)
    matched_skills: list[str]            # 匹配技能列表
    missing_skills: list[str]            # 缺失技能列表
    recommendation: str                  # 匹配建议

# ========== 核心函数 ==========
async def analyze_resume(text: str, validation_feedback: str | None = None):
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY 未配置")

    # ===== 第一层防护：Prompt 约束 =====
    feedback_prompt = ""
    if validation_feedback:
        feedback_prompt = f"""
        上一轮输出未通过 Pydantic 校验，请根据以下错误修正：
        {validation_feedback}
        只输出修正后的完整 JSON，不要输出解释。
        """

    prompt = f"""
        下面这段文字请判断一下作者的情绪，（正面/负面/中性）
        请一步步推理，先分析理由，再给结论。
        要求输出 JSON 格式：{{"reasoning": "分析理由", "sentiment": "positive/negative/neutral"}}
        内容如下：{text}
        """

    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            "https://api.deepseek.com/chat/completions",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "response_format": {"type": "json_object"},
                "stream": True,
            },
            timeout=60.0,
        ) as response:
            response.raise_for_status()

            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data_str = line[6:]  # 去掉 "data: " 前缀
                    if data_str.strip() == "[DONE]":
                        break
                    chunk = json.loads(data_str)
                    delta = chunk["choices"][0]["delta"]
                    if "content" in delta:
                        yield delta["content"]


# ========== 重试机制 ==========
async def analyze_resume_with_retry(text: str, max_retries: int = 3):
    validation_feedback = None
    for attempt in range(max_retries):
        try:
            async for chunk in analyze_resume(text, validation_feedback):
                yield chunk
            return  # 成功后直接返回
        except ValidationError as e:
            if attempt == max_retries - 1:
                raise
            validation_feedback = str(e)
            print(f"第{attempt+1}次校验失败，重试...")
    raise RuntimeError("重试次数用尽")

                        
# ========== 测试入口 ==========
async def main():
    resume = """
        昨晚喝到1点多回的家，到家就睡了。喝酒的时候，小杨发微信问我几点回去，我没听到手机响光喝酒了，没及时回，她生气了。
        上午龙哥发信息说是约25号那天出海捞皮皮虾，我想给小杨打电话问问要不要咱们一家三口一起去，可是电话她不接，信息也不回，她说因为我昨晚没回她消息，于是她也不回我消息。她说她不想去让我带洛汐我俩去，后来我也生气了，我回复了龙哥说：就我一个人。
        我和小杨在微信上吵了几句，她总觉得我既然不上班了就应该每天多陪孩子，而我觉得虽然我不上班了，但是我需要每天来书店学习，而且我并没有不陪孩子。每次下楼玩其他宝妈带着孩子，小杨和她们说说笑笑，洛汐自己玩自己的，我站在那里就很尴尬也不知道做什么。除了下楼玩，我其他的事情都有做，在家我也有陪洛汐玩，但是小杨并不满意，好像无论我做的好与不好她都会生气。只要我出去做其他事，她就是会不高兴，总会找一些理由来闹别扭。我好心累，我不想和她吵了，以后我也不想管她的情绪如何，我该做我的事就每天按部就班做我的事吧。
        立全花钱买了教程课，貌似还可以，他正在全心投入到学习中，我也应该好好学学了。可是昨天喝完酒今天状态确实不好，头晕晕的，记忆力也不清晰，脑子很浑浊。但是我也不想回家，我不想回去面对情绪不好的家，我自己在书店呆着挺好的。
    """

    result = analyze_resume_with_retry(resume)
    print("\n[流式输出结果]")
    async for chunk in result:
        print(chunk, end="", flush=True)
    print()


if __name__ == "__main__":
    asyncio.run(main())
