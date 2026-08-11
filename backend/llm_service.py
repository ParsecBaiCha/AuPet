# -*- coding: utf-8 -*-
"""DeepSeek 大语言模型服务模块
提供对话、出题、绘本生成、动画代码生成等功能。
"""
import os
import json
import requests

# 优先从本地配置文件读取（不提交到GitHub），其次从环境变量读取
try:
    from config_local import DEEPSEEK_API_KEY
except ImportError:
    DEEPSEEK_API_KEY = os.environ.get('DEEPSEEK_API_KEY', '')
DEEPSEEK_BASE_URL = 'https://api.deepseek.com/v1'
MODEL = 'deepseek-chat'

# ---------- 年级自适应提示词 ----------
GRADE_PROMPTS = {
    'lower_primary': (
        '你是一个面向小学低年级（1-3年级）学生的AI老师。'
        '请用简单、活泼、有趣的语言教学，多用比喻和生活中的例子。'
        '每次回答不超过200字。'
        '重要：不要使用任何emoji表情符号，不要使用特殊符号，只用纯文字回答。'
        '如果学生问的问题超出AI通识课范围，引导他们回到学习话题。'
    ),
    'upper_primary': (
        '你是一个面向小学高年级（4-6年级）学生的AI老师。'
        '请用通俗易懂的语言教学，适当引入简单的编程概念。'
        '每次回答不超过300字，可以用代码示例但需要详细注释。'
        '重要：不要使用任何emoji表情符号，不要使用特殊符号，只用纯文字回答。'
        '鼓励学生动手实践，多提问引导思考。'
    ),
    'middle_school': (
        '你是一个面向初中生的AI老师。'
        '请用较专业的语言教学，可以涉及算法原理和编程实践。'
        '每次回答不超过400字，代码示例用Python，需要完整可运行。'
        '重要：不要使用任何emoji表情符号，不要使用特殊符号，只用纯文字回答。'
        '引导学生理解原理而非死记硬背。'
    ),
    'high_school': (
        '你是一个面向高中生的AI老师。'
        '请用专业、严谨的语言教学，深入讲解算法原理和AI模型结构。'
        '每次回答不超过500字，代码示例用Python，涉及机器学习框架。'
        '重要：不要使用任何emoji表情符号，不要使用特殊符号，只用纯文字回答。'
        '鼓励项目式学习和深度思考。'
    ),
}

GRADE_NAMES = {
    'lower_primary': '小学低年级',
    'upper_primary': '小学高年级',
    'middle_school': '初中',
    'high_school': '高中',
}


def _call_api(messages, temperature=0.7, max_tokens=1024):
    """调用 DeepSeek API"""
    try:
        resp = requests.post(
            f'{DEEPSEEK_BASE_URL}/chat/completions',
            headers={
                'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'model': MODEL,
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens,
                'stream': False,
            },
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        return data['choices'][0]['message']['content']
    except requests.exceptions.Timeout:
        return '抱歉，我思考得太久了，请再问一次吧～'
    except Exception as e:
        return f'（AI服务暂时不可用：{str(e)[:50]}）'


def chat(user_message, grade_level='upper_primary', history=None, pet_name='球球'):
    """AI对话问答 — 核心对话功能

    Args:
        user_message: 学生发送的消息
        grade_level: 年级段
        history: 历史对话 [{'role': 'user'|'assistant', 'content': '...'}]
        pet_name: 宠物名字，用于个性化称呼
    """
    system_prompt = GRADE_PROMPTS.get(grade_level, GRADE_PROMPTS['upper_primary'])
    system_prompt += f'\n你的名字是{pet_name}，是学生的AI学习伙伴。学生称呼你为{pet_name}。'
    system_prompt += '\n你主要负责教授人工智能通识课，包括：什么是AI、机器学习基础、编程入门、算法思维等。'
    system_prompt += '\n如果学生情绪低落，也可以给予情感支持，但重点还是引导学习。'

    messages = [{'role': 'system', 'content': system_prompt}]
    if history:
        for h in history[-6:]:  # 保留最近6条历史
            messages.append({'role': h.get('role', 'user'), 'content': h.get('content', '')})
    messages.append({'role': 'user', 'content': user_message})

    return _call_api(messages, temperature=0.8)


def generate_quiz(topic, grade_level='upper_primary', count=3):
    """游戏化练习 — 自动生成测验题目

    Returns: list of {'question': str, 'options': list[str], 'answer': int, 'explanation': str}
    """
    grade_name = GRADE_NAMES.get(grade_level, '小学高年级')
    system_prompt = (
        f'你是一个面向{grade_name}学生的AI出题老师。'
        f'请围绕知识点「{topic}」生成{count}道选择题。'
        '每题4个选项，标注正确答案的序号(0-3)，并给出简短解析。'
        '请严格按照JSON数组格式输出，不要输出其他内容。'
        '格式：[{"question":"题目","options":["A","B","C","D"],"answer":0,"explanation":"解析"}]'
    )
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': f'请生成关于「{topic}」的{count}道选择题'},
    ]
    raw = _call_api(messages, temperature=0.5, max_tokens=2048)

    # 尝试解析JSON
    try:
        # 去除可能的markdown代码块标记
        raw = raw.strip()
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[1] if '\n' in raw else raw[3:]
        if raw.endswith('```'):
            raw = raw[:-3]
        raw = raw.strip()
        if raw.startswith('json'):
            raw = raw[4:].strip()
        return json.loads(raw)
    except (json.JSONDecodeError, IndexError):
        return [{'question': '题目生成失败，请重试', 'options': ['A', 'B', 'C', 'D'],
                 'answer': 0, 'explanation': raw[:100]}]


def grade_quiz(questions, answers):
    """批改测验 — 简单对比答案"""
    correct = 0
    results = []
    for i, q in enumerate(questions):
        user_answer = answers[i] if i < len(answers) else -1
        is_correct = user_answer == q.get('answer', -1)
        if is_correct:
            correct += 1
        results.append({
            'question': q.get('question', ''),
            'userAnswer': user_answer,
            'correctAnswer': q.get('answer', -1),
            'isCorrect': is_correct,
            'explanation': q.get('explanation', ''),
        })
    return {
        'total': len(questions),
        'correct': correct,
        'score': round(correct / max(len(questions), 1) * 100),
        'details': results,
    }


def generate_picture_book(topic, grade_level='lower_primary'):
    """绘本生成 — 面向低龄学生

    Returns: {'title': str, 'pages': [{'text': str, 'svg': str}]}
    """
    grade_name = GRADE_NAMES.get(grade_level, '小学低年级')
    system_prompt = (
        f'你是一个面向{grade_name}学生的绘本创作AI。'
        f'请围绕知识点「{topic}」创作一个5页的互动绘本。'
        '每页包含：一段50字以内的故事文字，和一个SVG插图代码。'
        'SVG要求：200x200画布，使用简单的几何图形和鲜艳的颜色，适合儿童。'
        '请严格按照JSON格式输出，不要输出其他内容。'
        '格式：{"title":"绘本标题","pages":[{"text":"文字","svg":"<svg>...</svg>"}]}'
    )
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': f'请创作关于「{topic}」的绘本'},
    ]
    raw = _call_api(messages, temperature=0.9, max_tokens=4096)

    try:
        raw = raw.strip()
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[1] if '\n' in raw else raw[3:]
        if raw.endswith('```'):
            raw = raw[:-3]
        raw = raw.strip()
        if raw.startswith('json'):
            raw = raw[4:].strip()
        book = json.loads(raw)
        if 'title' not in book or 'pages' not in book:
            raise ValueError('格式不完整')
        return book
    except (json.JSONDecodeError, ValueError):
        return {
            'title': f'{topic}的绘本',
            'pages': [{'text': '绘本生成失败，请重试', 'svg': '<svg viewBox="0 0 200 200"><circle cx="100" cy="100" r="50" fill="#f48d45"/></svg>'}],
        }


def generate_animation(topic, grade_level='upper_primary'):
    """动画讲解 — 生成SVG动画代码讲解抽象概念

    Returns: {'title': str, 'description': str, 'svg': str, 'explanation': str}
    """
    grade_name = GRADE_NAMES.get(grade_level, '小学高年级')
    system_prompt = (
        f'你是一个面向{grade_name}学生的算法可视化AI老师。'
        f'请为知识点「{topic}」生成一个SVG动画来直观讲解。'
        'SVG要求：800x400画布，使用<animate>标签实现动画效果，颜色鲜艳。'
        '同时给出文字解释，帮助学生理解。'
        '请严格按照JSON格式输出，不要输出其他内容。'
        '格式：{"title":"标题","description":"简短描述","svg":"<svg>...</svg>","explanation":"详细解释"}'
    )
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': f'请为「{topic}」生成动画讲解'},
    ]
    raw = _call_api(messages, temperature=0.7, max_tokens=4096)

    try:
        raw = raw.strip()
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[1] if '\n' in raw else raw[3:]
        if raw.endswith('```'):
            raw = raw[:-3]
        raw = raw.strip()
        if raw.startswith('json'):
            raw = raw[4:].strip()
        result = json.loads(raw)
        if 'svg' not in result:
            raise ValueError('格式不完整')
        return result
    except (json.JSONDecodeError, ValueError):
        return {
            'title': f'{topic}动画讲解',
            'description': '动画生成失败，请重试',
            'svg': '<svg viewBox="0 0 800 400"><text x="400" y="200" text-anchor="middle" font-size="24" fill="#999">动画生成中...</text></svg>',
            'explanation': raw[:200] if raw else '',
        }


def generate_learning_suggestion(grade_level, learned_topics, quiz_scores):
    """个性化学习路径 — 根据学习记录生成下一步建议"""
    grade_name = GRADE_NAMES.get(grade_level, '小学高年级')
    system_prompt = (
        f'你是一个面向{grade_name}学生的AI学习路径规划师。'
        f'学生已学知识点：{", ".join(learned_topics) if learned_topics else "暂无"}。'
        f'最近测验得分：{quiz_scores if quiz_scores else "暂无"}。'
        '请根据学生情况，推荐下一步应该学习的2-3个知识点，并说明原因。'
        '请用JSON格式输出：{"suggestions":[{"topic":"知识点","reason":"推荐原因","difficulty":"easy|medium|hard"}]}'
    )
    messages = [
        {'role': 'system', 'content': system_prompt},
        {'role': 'user', 'content': '请推荐下一步学习内容'},
    ]
    raw = _call_api(messages, temperature=0.6, max_tokens=1024)

    try:
        raw = raw.strip()
        if raw.startswith('```'):
            raw = raw.split('\n', 1)[1] if '\n' in raw else raw[3:]
        if raw.endswith('```'):
            raw = raw[:-3]
        raw = raw.strip()
        if raw.startswith('json'):
            raw = raw[4:].strip()
        return json.loads(raw)
    except json.JSONDecodeError:
        return {'suggestions': [{'topic': '继续学习', 'reason': raw[:100], 'difficulty': 'easy'}]}
