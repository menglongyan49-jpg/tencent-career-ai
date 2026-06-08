import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Map,
  ChevronRight,
  Check,
  Clock,
  Target,
  Lightbulb,
  BookOpen,
  Award,
  TrendingUp,
} from 'lucide-react'
import { useUserStore, getGradeName } from '../store/userStore'
import GooseMascot from '../components/GooseMascot'

const PATH_STAGES = {
  freshman: [
    {
      title: '认知启蒙期',
      desc: '了解互联网行业，建立基础认知',
      tasks: [
        { name: '了解互联网行业概况', points: 20 },
        { name: '认识腾讯主要业务线', points: 20 },
        { name: '探索1-2个感兴趣的方向', points: 30 },
        { name: '制定大学四年成长规划', points: 30 },
      ],
    },
    {
      title: '基础积累期',
      desc: '打好专业基础，培养核心能力',
      tasks: [
        { name: '学好专业核心课程', points: 30 },
        { name: '培养一项技术/设计技能', points: 40 },
        { name: '参加1个学生组织/社团', points: 20 },
        { name: '阅读3本行业相关书籍', points: 30 },
      ],
    },
  ],
  sophomore: [
    {
      title: '方向探索期',
      desc: '明确职业方向，开始实践探索',
      tasks: [
        { name: '确定1-2个职业方向', points: 30 },
        { name: '完成1个小项目实践', points: 40 },
        { name: '参加行业讲座/分享会', points: 20 },
        { name: '建立学习笔记/作品集', points: 30 },
      ],
    },
    {
      title: '能力提升期',
      desc: '深化专业技能，积累项目经验',
      tasks: [
        { name: '深入学习核心技能', points: 40 },
        { name: '参加比赛/竞赛', points: 50 },
        { name: '寻找导师/学长指导', points: 20 },
        { name: '关注行业动态', points: 20 },
      ],
    },
  ],
  junior: [
    {
      title: '实习准备期',
      desc: '准备实习申请，提升竞争力',
      tasks: [
        { name: '完善简历', points: 30 },
        { name: '准备面试常见问题', points: 30 },
        { name: '了解目标公司/岗位', points: 20 },
        { name: '模拟面试练习', points: 40 },
      ],
    },
    {
      title: '实习冲刺期',
      desc: '获得实习机会，积累实战经验',
      tasks: [
        { name: '投递暑期实习', points: 30 },
        { name: '完成实习面试', points: 40 },
        { name: '获得实习offer', points: 100 },
        { name: '实习期间表现优秀', points: 80 },
      ],
    },
  ],
  senior: [
    {
      title: '求职冲刺期',
      desc: '全力准备秋招/春招',
      tasks: [
        { name: '优化简历和作品集', points: 30 },
        { name: '刷题/准备技术面试', points: 50 },
        { name: '投递目标公司', points: 30 },
        { name: '参加校园招聘', points: 40 },
      ],
    },
    {
      title: '职业启航期',
      desc: '拿到心仪offer，开启职业生涯',
      tasks: [
        { name: '获得面试机会', points: 50 },
        { name: '通过终面', points: 80 },
        { name: '拿到心仪offer', points: 150 },
        { name: '完成入职准备', points: 50 },
      ],
    },
  ],
  graduate: [
    {
      title: '研究方向期',
      desc: '深耕专业领域，产出研究成果',
      tasks: [
        { name: '确定研究方向', points: 30 },
        { name: '发表论文/专利', points: 80 },
        { name: '参加学术会议', points: 40 },
        { name: '完成研究项目', points: 60 },
      ],
    },
    {
      title: '职业选择期',
      desc: '选择就业或深造，规划未来',
      tasks: [
        { name: '明确职业规划', points: 30 },
        { name: '准备求职/申博', points: 40 },
        { name: '获得心仪机会', points: 100 },
        { name: '完成毕业答辩', points: 80 },
      ],
    },
  ],
}

const TIPS = [
  {
    icon: Lightbulb,
    title: '保持学习',
    desc: '技术更新快，持续学习是关键',
  },
  {
    icon: BookOpen,
    title: '注重实践',
    desc: '项目经验比理论知识更重要',
  },
  {
    icon: Award,
    title: '积累作品',
    desc: '作品集是能力的最好证明',
  },
  {
    icon: TrendingUp,
    title: '关注趋势',
    desc: '了解行业动态，把握机会',
  },
]

const PathPage: React.FC = () => {
  const { profile, level } = useUserStore()
  const [activeStage, setActiveStage] = useState(0)

  const grade = profile?.grade || 'freshman'
  const stages = PATH_STAGES[grade] || PATH_STAGES.freshman

  return (
    <div className="min-h-screen pb-20">
      {/* 头部 */}
      <div className="bg-gradient-to-br from-purple-500 to-indigo-600 text-white p-6">
        <div className="flex items-center gap-3 mb-4">
          <Map size={24} />
          <h1 className="text-xl font-bold">成长路径</h1>
        </div>
        <p className="text-white/80">
          {profile ? `${getGradeName(grade)}的专属成长规划` : '个性化职业成长路径'}
        </p>
      </div>

      {/* 当前状态卡片 */}
      <div className="px-4 -mt-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl p-5 shadow-lg"
        >
          <div className="flex items-center gap-4">
            <GooseMascot size={50} />
            <div className="flex-1">
              <p className="font-bold">当前阶段</p>
              <p className="text-sm text-gray-500">
                {stages[activeStage]?.title || '认知启蒙期'}
              </p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-purple-600">Lv.{level}</p>
              <p className="text-xs text-gray-400">成长等级</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* 阶段选择 */}
      <div className="px-4 mt-6">
        <h2 className="font-bold mb-3">成长阶段</h2>
        <div className="flex gap-2 overflow-x-auto pb-2">
          {stages.map((stage, index) => (
            <button
              key={stage.title}
              onClick={() => setActiveStage(index)}
              className={`flex-shrink-0 px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                activeStage === index
                  ? 'bg-purple-500 text-white'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {stage.title}
            </button>
          ))}
        </div>
      </div>

      {/* 任务列表 */}
      <div className="px-4 mt-6">
        <motion.div
          key={activeStage}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="bg-white rounded-2xl overflow-hidden"
        >
          <div className="p-4 bg-gradient-to-r from-purple-50 to-indigo-50 border-b border-gray-100">
            <h3 className="font-bold">{stages[activeStage]?.title}</h3>
            <p className="text-sm text-gray-500">{stages[activeStage]?.desc}</p>
          </div>

          <div className="divide-y divide-gray-100">
            {stages[activeStage]?.tasks.map((task, index) => (
              <div
                key={task.name}
                className="flex items-center gap-3 p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center text-sm font-medium">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <p className="font-medium text-sm">{task.name}</p>
                  <p className="text-xs text-gray-400">+{task.points} 积分</p>
                </div>
                <button className="p-2 bg-purple-50 text-purple-600 rounded-lg hover:bg-purple-100 transition-colors">
                  <Check size={16} />
                </button>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* 成长建议 */}
      <div className="px-4 mt-6">
        <h2 className="font-bold mb-3">成长建议</h2>
        <div className="grid grid-cols-2 gap-3">
          {TIPS.map((tip, index) => (
            <motion.div
              key={tip.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl p-4"
            >
              <tip.icon className="text-purple-500 mb-2" size={20} />
              <p className="font-medium text-sm">{tip.title}</p>
              <p className="text-xs text-gray-400 mt-1">{tip.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* 时间线预览 */}
      <div className="px-4 mt-6">
        <h2 className="font-bold mb-3">成长时间线</h2>
        <div className="bg-white rounded-2xl p-4">
          <div className="relative">
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-gray-200" />
            <div className="space-y-4">
              {stages.map((stage, index) => (
                <div key={stage.title} className="flex items-start gap-4">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center z-10 ${
                      index <= activeStage
                        ? 'bg-purple-500 text-white'
                        : 'bg-gray-200 text-gray-400'
                    }`}
                  >
                    {index + 1}
                  </div>
                  <div className="flex-1 pt-1">
                    <p className={`font-medium text-sm ${index <= activeStage ? 'text-gray-800' : 'text-gray-400'}`}>
                      {stage.title}
                    </p>
                    <p className="text-xs text-gray-400">{stage.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PathPage