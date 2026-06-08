interface ChatContext {
  grade?: string
  major?: string
  interests?: string[]
  goals?: string[]
}

// AI 对话服务
export async function chatWithAI(message: string, context?: ChatContext): Promise<string> {
  // 构建系统提示词
  const systemPrompt = buildSystemPrompt(context)

  // 调用大模型 API（这里使用模拟响应）
  // 实际部署时替换为真实的 AI API 调用
  return generateMockResponse(message, context)
}

function buildSystemPrompt(context?: ChatContext): string {
  let prompt = `你是"未来鹅"，一个面向大学生的职业成长AI陪伴体。你的任务是：

1. 帮助学生了解互联网行业和腾讯
2. 提供个性化的职业成长建议
3. 解答求职相关的困惑
4. 给予情感支持和鼓励

你的性格特点：
- 温暖、友好、有耐心
- 专业但不生硬
- 善于倾听和引导
- 会用适当的emoji增加亲和力

请用简洁、清晰的语言回答问题，必要时使用markdown格式。`

  if (context) {
    prompt += `\n\n用户背景信息：`
    if (context.grade) {
      const gradeNames: Record<string, string> = {
        freshman: '大一',
        sophomore: '大二',
        junior: '大三',
        senior: '大四',
        graduate: '研究生',
      }
      prompt += `\n- 年级：${gradeNames[context.grade] || context.grade}`
    }
    if (context.major) {
      prompt += `\n- 专业：${context.major}`
    }
    if (context.interests?.length) {
      prompt += `\n- 兴趣方向：${context.interests.join('、')}`
    }
    if (context.goals?.length) {
      prompt += `\n- 成长目标：${context.goals.join('、')}`
    }
  }

  return prompt
}

function generateMockResponse(message: string, context?: ChatContext): string {
  const lowerMessage = message.toLowerCase()

  // 根据用户背景和问题生成个性化响应
  if (lowerMessage.includes('实习') || lowerMessage.includes('暑期')) {
    return generateInternshipResponse(context)
  }

  if (lowerMessage.includes('简历')) {
    return generateResumeResponse()
  }

  if (lowerMessage.includes('面试')) {
    return generateInterviewResponse()
  }

  if (lowerMessage.includes('腾讯') || lowerMessage.includes('鹅厂')) {
    return generateTencentResponse()
  }

  if (lowerMessage.includes('方向') || lowerMessage.includes('迷茫')) {
    return generateDirectionResponse(context)
  }

  // 默认响应
  return `你好呀！我是未来鹅 🦆

很高兴能陪伴你的职业成长之旅！我可以帮你：

- 🎯 **职业规划**：分析适合你的方向，制定成长计划
- 💼 **求职准备**：简历优化、面试技巧、模拟练习
- 🏢 **行业认知**：了解互联网公司和岗位
- 💡 **能力提升**：推荐学习资源，规划技能路径

有什么想聊的吗？可以直接问我任何关于职业发展的问题！`
}

function generateInternshipResponse(context?: ChatContext): string {
  const grade = context?.grade || 'junior'
  const interests = context?.interests || []

  let response = `关于实习准备，我来给你一些建议 📚\n\n`

  if (grade === 'freshman' || grade === 'sophomore') {
    response += `**现阶段建议：**
- 打好专业基础，保持良好的GPA
- 学习一项核心技能（编程/设计/产品等）
- 参加1-2个学生组织或社团活动
- 尝试做一些小项目积累经验

大一/大二主要是打基础，不用太着急找实习。`
  } else {
    response += `**实习申请时间线：**
- **3-4月**：暑期实习网申开始
- **4-5月**：笔试面试高峰期
- **5-6月**：收offer，准备入职
- **7-8月**：暑期实习期

**准备建议：**
1. 完善简历，突出项目经历
2. 刷题/准备技术面试
3. 了解目标岗位的业务
4. 准备行为面试问题`
  }

  if (interests.length > 0) {
    response += `\n\n基于你对**${interests[0]}**的兴趣，建议关注相关岗位的实习机会。`
  }

  return response
}

function generateResumeResponse(): string {
  return `简历优化建议 📄

**一份好简历的关键要素：**

1. **清晰的个人信息**
   - 姓名、联系方式、求职意向

2. **教育背景**
   - 学校、专业、GPA（如果好的话）
   - 相关课程、荣誉奖项

3. **项目经历**（最重要！）
   - 使用STAR法则描述
   - 量化成果和数据
   - 突出你的贡献

4. **技能清单**
   - 与岗位匹配的关键技能
   - 熟练程度标注

5. **其他加分项**
   - 比赛/竞赛获奖
   - 开源项目/作品集
   - 实习/实践经历

**常见问题：**
- ❌ 描述太笼统，没有具体内容
- ❌ 没有量化成果
- ❌ 与目标岗位不匹配

需要我帮你具体分析简历吗？可以在"求职助手"模块上传简历！`
}

function generateInterviewResponse(): string {
  return `面试准备攻略 🎯

**面试类型：**

1. **技术面试**
   - 算法/数据结构
   - 系统设计
   - 项目深挖

2. **行为面试**
   - 自我介绍
   - 项目经历讲述
   - 团队协作案例

3. **HR面试**
   - 职业规划
   - 为什么选择我们
   - 薪资期望

**准备建议：**

✅ **技术准备**
- 刷LeetCode常见题型
- 复习计算机基础
- 准备项目技术细节

✅ **行为准备**
- 准备3-5个核心故事
- 使用STAR法则组织
- 提前练习讲述

✅ **公司了解**
- 研究目标岗位JD
- 了解业务和产品
- 准备有深度的问题

要不要在"求职助手"里进行一次模拟面试练习？`
}

function generateTencentResponse(): string {
  return `关于腾讯（鹅厂）🐧

**腾讯是中国领先的互联网科技公司**，业务覆盖社交、游戏、云服务、内容等多个领域。

**主要事业群：**

📱 **微信事业群（WXG）**
- 微信、企业微信、微信支付

🎮 **游戏事业群（IEG）**
- 王者荣耀、和平精英、英雄联盟手游

☁️ **云与智慧产业事业群（CSIG）**
- 腾讯云、腾讯会议

📺 **平台与内容事业群（PCG）**
- QQ、腾讯视频、腾讯新闻

⚙️ **技术工程事业群（TEG）**
- AI Lab、安全平台

**为什么选择腾讯：**
- 技术氛围浓厚，大佬云集
- 完善的培养体系
- 有竞争力的薪酬福利
- 广阔的成长空间

想了解某个具体业务或岗位吗？可以在"鹅厂探秘"模块深入探索！`
}

function generateDirectionResponse(context?: ChatContext): string {
  const interests = context?.interests || []
  const major = context?.major || ''

  let response = `职业方向选择确实是一个需要认真思考的问题 🤔\n\n`

  if (major) {
    response += `作为**${major}**专业的学生，`
  }
  response += `你可以从以下几个维度来思考：\n\n`

  response += `**1. 兴趣驱动**
- 你平时喜欢做什么？
- 什么事情让你有成就感？

**2. 能力匹配**
- 你擅长什么？
- 有哪些可迁移的技能？

**3. 市场需求**
- 行业发展趋势如何？
- 哪些岗位需求量大？

**4. 价值取向**
- 你看重什么？薪资/成长/稳定/意义？`

  if (interests.length > 0) {
    response += `\n\n你提到对**${interests.join('、')}**感兴趣，这是很好的起点！建议你：`
    response += `\n1. 深入了解这些方向的具体工作内容`
    response += `\n2. 尝试相关的项目或实习`
    response += `\n3. 和在这个领域工作的人交流`
  }

  response += `\n\n如果还是不确定，可以来"成长路径"模块，我会根据你的情况帮你规划！`

  return response
}

// 获取推荐问题
export function getChatSuggestions(): string[] {
  return [
    '腾讯有哪些岗位适合我？',
    '如何准备暑期实习面试？',
    '简历应该怎么写？',
    '产品经理需要什么能力？',
    '技术岗的面试流程是怎样的？',
    '大一应该做哪些准备？',
  ]
}