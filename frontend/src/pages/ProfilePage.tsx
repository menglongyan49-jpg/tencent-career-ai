import React from 'react'
import { motion } from 'framer-motion'
import {
  User,
  Edit3,
  Award,
  TrendingUp,
  Calendar,
  BookOpen,
  Star,
  ChevronRight,
} from 'lucide-react'
import { useUserStore, getGradeName } from '../store/userStore'
import GooseMascot from '../components/GooseMascot'

const ProfilePage: React.FC = () => {
  const { profile, level, totalPoints, growthRecords } = useUserStore()

  if (!profile) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p>请先完成个人信息</p>
      </div>
    )
  }

  const levelProgress = () => {
    const thresholds = [0, 100, 300, 600, 1000, 1500]
    const currentThreshold = thresholds[level - 1] || 0
    const nextThreshold = thresholds[level] || thresholds[thresholds.length - 1]
    const progress = ((totalPoints - currentThreshold) / (nextThreshold - currentThreshold)) * 100
    return Math.min(100, Math.max(0, progress))
  }

  const getLevelTitle = (lvl: number): string => {
    const titles = ['萌新小鹅', '探索小鹅', '成长小鹅', '进阶小鹅', '精英小鹅', '大师小鹅']
    return titles[Math.min(lvl - 1, titles.length - 1)]
  }

  return (
    <div className="min-h-screen pb-20">
      {/* 头部卡片 */}
      <div className="bg-gradient-to-br from-primary-500 to-blue-600 text-white p-6 pb-16">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-xl font-bold">我的成长档案</h1>
          <button className="p-2 bg-white/20 rounded-lg hover:bg-white/30 transition-colors">
            <Edit3 size={18} />
          </button>
        </div>

        <div className="flex items-center gap-4">
          <div className="w-20 h-20 rounded-full bg-white/20 flex items-center justify-center">
            <GooseMascot size={60} animate={false} />
          </div>
          <div>
            <h2 className="text-2xl font-bold">{profile.nickname}</h2>
            <p className="text-white/80">
              {getGradeName(profile.grade)} · {profile.major || '未设置专业'}
            </p>
            <p className="text-sm text-white/60">{profile.university || '未设置学校'}</p>
          </div>
        </div>
      </div>

      {/* 等级卡片 */}
      <div className="px-4 -mt-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl p-5 shadow-lg"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-goose-yellow to-goose-orange rounded-xl flex items-center justify-center">
                <Award className="text-white" size={24} />
              </div>
              <div>
                <p className="font-bold">Lv.{level} {getLevelTitle(level)}</p>
                <p className="text-sm text-gray-500">{totalPoints} 成长积分</p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-400">距离下一级</p>
              <p className="text-sm font-medium text-primary-600">{Math.round(levelProgress())}%</p>
            </div>
          </div>

          <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{ width: `${levelProgress()}%` }}
              transition={{ duration: 1, ease: 'easeOut' }}
              className="h-full bg-gradient-to-r from-goose-yellow to-goose-orange rounded-full"
            />
          </div>
        </motion.div>
      </div>

      {/* 兴趣标签 */}
      <div className="px-4 mt-6">
        <div className="bg-white rounded-2xl p-5">
          <h3 className="font-bold mb-3 flex items-center gap-2">
            <Star size={18} className="text-goose-yellow" />
            兴趣方向
          </h3>
          <div className="flex flex-wrap gap-2">
            {profile.interests.length > 0 ? (
              profile.interests.map((interest) => (
                <span
                  key={interest}
                  className="bg-primary-50 text-primary-700 px-3 py-1.5 rounded-full text-sm"
                >
                  {interest}
                </span>
              ))
            ) : (
              <span className="text-gray-400 text-sm">暂未设置兴趣方向</span>
            )}
          </div>
        </div>
      </div>

      {/* 目标 */}
      <div className="px-4 mt-4">
        <div className="bg-white rounded-2xl p-5">
          <h3 className="font-bold mb-3 flex items-center gap-2">
            <TrendingUp size={18} className="text-green-500" />
            成长目标
          </h3>
          <div className="space-y-2">
            {profile.goals.length > 0 ? (
              profile.goals.map((goal, index) => (
                <div
                  key={goal}
                  className="flex items-center gap-3 p-3 bg-green-50 rounded-xl"
                >
                  <div className="w-6 h-6 bg-green-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                    {index + 1}
                  </div>
                  <span className="text-sm">{goal}</span>
                </div>
              ))
            ) : (
              <span className="text-gray-400 text-sm">暂未设置成长目标</span>
            )}
          </div>
        </div>
      </div>

      {/* 成长记录 */}
      <div className="px-4 mt-4">
        <div className="bg-white rounded-2xl p-5">
          <h3 className="font-bold mb-3 flex items-center gap-2">
            <BookOpen size={18} className="text-purple-500" />
            成长记录
          </h3>

          {growthRecords.length > 0 ? (
            <div className="space-y-3">
              {growthRecords.map((record) => (
                <div
                  key={record.id}
                  className="flex items-center gap-3 p-3 bg-gray-50 rounded-xl"
                >
                  <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                    <Award size={20} className="text-purple-500" />
                  </div>
                  <div className="flex-1">
                    <p className="font-medium text-sm">{record.title}</p>
                    <p className="text-xs text-gray-500">{record.description}</p>
                  </div>
                  <span className="text-goose-orange font-bold">+{record.points}</span>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Calendar size={24} className="text-gray-400" />
              </div>
              <p className="text-gray-400 text-sm">还没有成长记录</p>
              <p className="text-gray-300 text-xs mt-1">完成任务后这里会更新</p>
            </div>
          )}
        </div>
      </div>

      {/* 快捷入口 */}
      <div className="px-4 mt-4">
        <div className="bg-white rounded-2xl overflow-hidden">
          <button className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors">
            <div className="flex items-center gap-3">
              <User size={18} className="text-gray-400" />
              <span>编辑个人信息</span>
            </div>
            <ChevronRight size={18} className="text-gray-400" />
          </button>
          <div className="h-px bg-gray-100" />
          <button className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors">
            <div className="flex items-center gap-3">
              <Award size={18} className="text-gray-400" />
              <span>我的成就</span>
            </div>
            <ChevronRight size={18} className="text-gray-400" />
          </button>
          <div className="h-px bg-gray-100" />
          <button className="w-full flex items-center justify-between p-4 hover:bg-gray-50 transition-colors">
            <div className="flex items-center gap-3">
              <Calendar size={18} className="text-gray-400" />
              <span>校招日历</span>
            </div>
            <ChevronRight size={18} className="text-gray-400" />
          </button>
        </div>
      </div>
    </div>
  )
}

export default ProfilePage