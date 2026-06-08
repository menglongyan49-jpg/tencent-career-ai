import React from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  MessageCircle,
  Compass,
  Map,
  Briefcase,
  Target,
  Sparkles,
  ArrowRight,
  TrendingUp,
  Users,
  Lightbulb,
} from 'lucide-react'
import { useUserStore, getGradeName } from '../store/userStore'
import GooseMascot from '../components/GooseMascot'

const features = [
  {
    icon: MessageCircle,
    title: '智能问答',
    description: '随时解答职业困惑，了解互联网行业与鹅厂',
    path: '/chat',
    color: 'bg-blue-500',
  },
  {
    icon: Compass,
    title: '鹅厂探秘',
    description: '沉浸式探索腾讯业务、文化与员工故事',
    path: '/explorer',
    color: 'bg-green-500',
  },
  {
    icon: Map,
    title: '成长路径',
    description: '个性化职业成长规划，清晰每一步',
    path: '/path',
    color: 'bg-purple-500',
  },
  {
    icon: Briefcase,
    title: '求职助手',
    description: '简历优化、模拟面试，提升求职成功率',
    path: '/jobs',
    color: 'bg-orange-500',
  },
  {
    icon: Target,
    title: '成长任务',
    description: '任务驱动成长，积累经验与积分',
    path: '/quests',
    color: 'bg-pink-500',
  },
]

const stats = [
  { icon: Users, value: '10,000+', label: '小鹅在成长' },
  { icon: TrendingUp, value: '95%', label: '用户满意度' },
  { icon: Lightbulb, value: '500+', label: '职业知识点' },
]

const HomePage: React.FC = () => {
  const { profile, isOnboarded, level, totalPoints } = useUserStore()

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-12 lg:py-20 px-4">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-goose-yellow/20 rounded-full blur-3xl" />
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-blue-200/20 rounded-full blur-3xl" />
        </div>

        <div className="relative max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', duration: 0.8 }}
            className="mb-6"
          >
            <GooseMascot size={80} />
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-3xl lg:text-5xl font-bold mb-4"
          >
            <span className="gradient-text">你好{profile?.nickname ? `，${profile.nickname}` : ''}！</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="text-lg lg:text-xl text-gray-600 mb-8"
          >
            {profile ? (
              <>
                你是{getGradeName(profile.grade)}的{profile.major}学生
                {profile.interests.length > 0 && `，对${profile.interests.slice(0, 2).join('、')}感兴趣`}
              </>
            ) : (
              '陪伴每一只小鹅，飞向更远的未来'
            )}
          </motion.p>

          {/* 快速入口 */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="flex flex-wrap justify-center gap-4 mb-12"
          >
            <Link
              to="/chat"
              className="inline-flex items-center gap-2 bg-primary-500 hover:bg-primary-600 text-white px-6 py-3 rounded-full font-medium transition-all shadow-lg shadow-primary-500/30 hover:shadow-xl hover:shadow-primary-500/40"
            >
              <MessageCircle size={20} />
              开始对话
              <ArrowRight size={16} />
            </Link>
            <Link
              to="/path"
              className="inline-flex items-center gap-2 bg-white hover:bg-gray-50 text-gray-700 px-6 py-3 rounded-full font-medium transition-all border border-gray-200"
            >
              <Map size={20} />
              查看成长路径
            </Link>
          </motion.div>

          {/* 用户数据卡片 */}
          {isOnboarded && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.5 }}
              className="inline-flex items-center gap-6 bg-white/80 backdrop-blur-sm rounded-2xl px-6 py-4 shadow-lg"
            >
              <div className="text-center">
                <p className="text-2xl font-bold text-primary-600">Lv.{level}</p>
                <p className="text-xs text-gray-500">成长等级</p>
              </div>
              <div className="w-px h-8 bg-gray-200" />
              <div className="text-center">
                <p className="text-2xl font-bold text-goose-orange">{totalPoints}</p>
                <p className="text-xs text-gray-500">累计积分</p>
              </div>
              <div className="w-px h-8 bg-gray-200" />
              <div className="text-center">
                <p className="text-2xl font-bold text-green-500">0</p>
                <p className="text-xs text-gray-500">完成任务</p>
              </div>
            </motion.div>
          )}
        </div>
      </section>

      {/* 功能卡片 */}
      <section className="py-12 px-4">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-2xl font-bold text-center mb-8">
            <Sparkles className="inline-block mr-2 text-goose-yellow" />
            核心功能
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {features.map((feature, index) => (
              <motion.div
                key={feature.path}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 * index }}
              >
                <Link
                  to={feature.path}
                  className="block bg-white rounded-2xl p-6 card-hover border border-gray-100 h-full"
                >
                  <div className={`w-12 h-12 ${feature.color} rounded-xl flex items-center justify-center mb-4`}>
                    <feature.icon size={24} className="text-white" />
                  </div>
                  <h3 className="font-bold text-lg mb-2">{feature.title}</h3>
                  <p className="text-gray-500 text-sm">{feature.description}</p>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* 数据展示 */}
      <section className="py-12 px-4 bg-gradient-to-r from-primary-50 to-blue-50">
        <div className="max-w-4xl mx-auto">
          <div className="grid grid-cols-3 gap-8 text-center">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 * index }}
              >
                <stat.icon className="mx-auto mb-2 text-primary-500" size={24} />
                <p className="text-2xl lg:text-3xl font-bold text-gray-800">{stat.value}</p>
                <p className="text-sm text-gray-500">{stat.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* 今日推荐 */}
      <section className="py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-2xl font-bold mb-6">今日推荐</h2>
          <div className="bg-gradient-to-r from-goose-yellow/20 to-orange-100/50 rounded-2xl p-6">
            <div className="flex items-start gap-4">
              <div className="w-16 h-16 bg-white rounded-xl flex items-center justify-center shadow-sm">
                <Lightbulb size={32} className="text-goose-orange" />
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-lg mb-2">了解腾讯产品经理的一天</h3>
                <p className="text-gray-600 text-sm mb-4">
                  通过真实的员工故事，了解产品经理的日常工作内容、能力要求和成长路径。
                </p>
                <Link
                  to="/explorer"
                  className="inline-flex items-center gap-1 text-primary-600 hover:text-primary-700 font-medium text-sm"
                >
                  立即探索 <ArrowRight size={14} />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}

export default HomePage