import { axiosInstance } from './config'
import { UserProfile } from '../store/userStore'

// AI 对话接口
export async function chatWithAI(message: string, profile: UserProfile | null): Promise<string> {
  try {
    const response = await axiosInstance.post('/api/chat', {
      message,
      context: {
        grade: profile?.grade,
        major: profile?.major,
        interests: profile?.interests,
        goals: profile?.goals,
      },
    })
    return response.data.response
  } catch (error) {
    console.error('AI chat error:', error)
    // 返回模拟响应用于演示
    return getMockResponse(message)
  }
}

// 模拟响应（用于演示）
function getMockResponse(message: string): string {
  const lowerMessage = message.toLowerCase()

  if (lowerMessage.includes('腾讯') && (lowerMessage.includes('岗位') || lowerMessage.includes('职位'))) {
    return `腾讯作为互联网大厂，提供丰富的岗位选择：

**技术类**
- 后端开发（Java/Go/C++）
- 前端开发（Web/小程序）
- 移动端开发（iOS/Android）
- 算法工程师（推荐/NLP/CV）

**产品类**
- 产品经理
- 产品运营
- 用户研究

**设计类**
- UI/UX设计师
- 视觉设计师
- 交互设计师

**其他**
- 游戏策划
- 市场营销
- 人力资源

建议你根据自己的专业背景和兴趣选择方向。想了解某个具体岗位吗？`
  }

  if (lowerMessage.includes('面试') || lowerMessage.includes('准备')) {
    return `面试准备建议：

**1. 了解岗位**
- 深入研究岗位JD
- 了解团队业务方向
- 关注行业动态

**2. 技能准备**
- 梳理核心技能点
- 准备项目经历讲述
- 练习常见面试题

**3. 软实力**
- 准备自我介绍
- 练习行为面试题（STAR法则）
- 准备有深度的问题

**4. 模拟练习**
- 可以在"求职助手"模块进行AI模拟面试
- 记录复盘每次练习

需要我帮你进行模拟面试吗？`
  }

  if (lowerMessage.includes('实习') || lowerMessage.includes('能力')) {
    return `大厂实习通常需要以下能力：

**通用能力**
- 学习能力：快速上手新领域
- 沟通协作：团队合作、表达清晰
- 问题解决：逻辑思维、主动思考

**技术岗额外要求**
- 扎实的编程基础
- 至少一门编程语言熟练
- 有项目经验加分

**产品岗额外要求**
- 产品思维和用户视角
- 数据分析能力
- 沟通协调能力

**加分项**
- 相关比赛获奖
- 开源项目贡献
- 个人项目/作品集

建议从现在开始有针对性地积累！`
  }

  if (lowerMessage.includes('趋势') || lowerMessage.includes('发展')) {
    return `互联网行业发展趋势：

**当前热点**
- AI大模型应用落地
- 云原生技术普及
- 短视频/直播持续增长
- 出海业务成为新增长点

**未来方向**
- AI+行业深度融合
- 元宇宙/虚拟现实探索
- 数字化转型加速
- 隐私计算与数据安全

**对求职的启示**
- 关注AI相关技能
- 保持技术敏感度
- 培养跨界思维
- 注重基础能力

想深入了解某个方向吗？`
  }

  return `这是个很好的问题！作为你的职业成长伙伴，我可以帮你：

🎯 **职业规划**
- 分析适合你的岗位方向
- 制定阶段性成长目标
- 探索互联网行业机会

💡 **能力提升**
- 了解岗位能力要求
- 获取学习资源推荐
- 规划技能成长路径

🚀 **求职准备**
- 简历优化建议
- 面试技巧指导
- 模拟面试练习

请告诉我你具体想了解什么，我会给出更详细的建议！`
}