import React, { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Target,
  CheckCircle,
  Clock,
  Star,
  Gift,
  ChevronRight,
  Trophy,
  Flame,
  Calendar,
} from 'lucide-react'
import { useUserStore } from '../store/userStore'
import GooseMascot from '../components/GooseMascot'

const DAILY_QUESTS = [
  { id: 1, title: '完成一次AI对话', points: 10, completed: false },
  { id: 2, title: '阅读一篇行业文章', points: 15, completed: false },
  { id: 3, title: '学习一个技能知识点', points: 20, completed: false },
]

const WEEKLY_QUESTS = [
  { id: 4, title: '完成3次AI对话', points: 50, progress: 1, total: 3 },
  { id: 5, title: '完成一次模拟面试', points: 80, progress: 0, total: 1 },
  { id: 6, title: '更新成长档案', points: 30, progress: 0, total: 1 },
]

const SPECIAL_QUESTS = [
  {
    id: 7,
    title: '鹅厂知识达人',
    desc: '完成所有业务板块探索',
    points: 200,
    progress: 2,
    total: 6,
    badge: '🏆',
  },
  {
    id: 8,
    title: '面试高手',
    desc: '完成5次模拟面试',
    points: 300,
    progress: 0,
    total: 5,
    badge: '🎯',
  },
  {
    id: 9,
    title: '成长先锋',
    desc: '累计获得1000积分',
    points: 500,
    progress: 320,
    total: 1000,
    badge: '⭐',
  },
]

const ACHIEVEMENTS = [
  { id: 1, name: '初来乍到', desc: '完成注册', icon: '🐣', unlocked: true },
  { id: 2, name: '探索者', desc: '完成首次鹅厂探秘', icon: '🧭', unlocked: true },
  { id: 3, name: '对话达人', desc: '完成10次AI对话', icon: '💬', unlocked: false },
  { id: 4, name: '面试新星', desc: '完成首次模拟面试', icon: '🎤', unlocked: false },
  { id: 5, name: '知识达人', desc: '解锁所有业务板块', icon: '📚', unlocked: false },
]

const QuestsPage: React.FC = () => {
  const { totalPoints, level, addPoints } = useUserStore()
  const [dailyQuests, setDailyQuests] = useState(DAILY_QUESTS)
  const [streak, setStreak] = useState(3)

  const handleCompleteQuest = (questId: number, points: number) => {
    setDailyQuests((quests) =>
      quests.map((q) => (q.id === questId ? { ...q, completed: true } : q))
    )
    addPoints(points)
  }

  const completedToday = dailyQuests.filter((q) => q.completed).length

  return (
    <div className="min-h-screen pb-20">
      {/* 头部 */}
      <div className="bg-gradient-to-br from-pink-500 to-rose-600 text-white p-6">
        <div className="flex items-center gap-3 mb-4">
          <Target size={24} />
          <h1 className="text-xl font-bold">成长任务</h1>
        </div>
        <p className="text-white/80">完成任务，积累积分，解锁成就</p>
      </div>

      {/* 积分卡片 */}
      <div className="px-4 -mt-4">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-2xl p-5 shadow-lg"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-gradient-to-br from-pink-400 to-rose-500 rounded-xl flex items-center justify-center">
                <Trophy className="text-white" size={28} />
              </div>
              <div>
                <p className="text-2xl font-bold">{totalPoints}</p>
                <p className="text-sm text-gray-500">总积分</p>
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-1 text-orange-500">
                <Flame size={18} />
                <span className="font-bold">{streak}</span>
              </div>
              <p className="text-xs text-gray-400">连续打卡</p>
            </div>
          </div>
        </motion.div>
      </div>

      {/* 每日任务 */}
      <div className="px-4 mt-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="font-bold flex items-center gap-2">
            <Calendar size={18} className="text-pink-500" />
            每日任务
          </h2>
          <span className="text-sm text-gray-400">
            {completedToday}/{dailyQuests.length} 已完成
          </span>
        </div>

        <div className="bg-white rounded-2xl overflow-hidden">
          {dailyQuests.map((quest, index) => (
            <div
              key={quest.id}
              className={`flex items-center justify-between p-4 ${
                index !== dailyQuests.length - 1 ? 'border-b border-gray-100' : ''
              }`}
            >
              <div className="flex items-center gap-3">
                <div
                  className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                    quest.completed
                      ? 'bg-green-100 text-green-500'
                      : 'bg-gray-100 text-gray-400'
                  }`}
                >
                  {quest.completed ? <CheckCircle size={18} /> : <Clock size={18} />}
                </div>
                <div>
                  <p className={`font-medium text-sm ${quest.completed ? 'text-gray-400 line-through' : ''}`}>
                    {quest.title}
                  </p>
                  <p className="text-xs text-gray-400">+{quest.points} 积分</p>
                </div>
              </div>
              {!quest.completed && (
                <button
                  onClick={() => handleCompleteQuest(quest.id, quest.points)}
                  className="px-3 py-1 bg-pink-50 text-pink-600 rounded-lg text-sm hover:bg-pink-100 transition-colors"
                >
                  完成
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* 周任务 */}
      <div className="px-4 mt-6">
        <h2 className="font-bold mb-3 flex items-center gap-2">
          <Star size={18} className="text-yellow-500" />
          周常任务
        </h2>

        <div className="space-y-3">
          {WEEKLY_QUESTS.map((quest) => (
            <div key={quest.id} className="bg-white rounded-xl p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="font-medium text-sm">{quest.title}</p>
                <span className="text-sm text-pink-500">+{quest.points}</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-pink-400 to-rose-500 rounded-full transition-all"
                    style={{ width: `${(quest.progress / quest.total) * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-400">
                  {quest.progress}/{quest.total}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 特殊成就任务 */}
      <div className="px-4 mt-6">
        <h2 className="font-bold mb-3 flex items-center gap-2">
          <Gift size={18} className="text-purple-500" />
          成就任务
        </h2>

        <div className="space-y-3">
          {SPECIAL_QUESTS.map((quest) => (
            <div key={quest.id} className="bg-white rounded-xl p-4">
              <div className="flex items-center gap-3 mb-2">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center text-xl">
                  {quest.badge}
                </div>
                <div className="flex-1">
                  <p className="font-medium text-sm">{quest.title}</p>
                  <p className="text-xs text-gray-400">{quest.desc}</p>
                </div>
                <span className="text-sm text-purple-500">+{quest.points}</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-purple-400 to-pink-500 rounded-full"
                    style={{ width: `${(quest.progress / quest.total) * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-400">
                  {quest.progress}/{quest.total}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 成就展示 */}
      <div className="px-4 mt-6">
        <h2 className="font-bold mb-3 flex items-center gap-2">
          <Trophy size={18} className="text-yellow-500" />
          我的成就
        </h2>

        <div className="bg-white rounded-2xl p-4">
          <div className="grid grid-cols-5 gap-3">
            {ACHIEVEMENTS.map((achievement) => (
              <div
                key={achievement.id}
                className={`text-center ${
                  !achievement.unlocked && 'opacity-40 grayscale'
                }`}
              >
                <div className="w-12 h-12 bg-gray-100 rounded-xl flex items-center justify-center mx-auto mb-1 text-xl">
                  {achievement.icon}
                </div>
                <p className="text-xs font-medium truncate">{achievement.name}</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 积分商城入口 */}
      <div className="px-4 mt-6">
        <div className="bg-gradient-to-r from-yellow-100 to-orange-100 rounded-2xl p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-white rounded-xl flex items-center justify-center">
              <Gift className="text-orange-500" size={24} />
            </div>
            <div>
              <p className="font-bold">积分商城</p>
              <p className="text-xs text-gray-500">用积分兑换专属福利</p>
            </div>
          </div>
          <ChevronRight className="text-gray-400" size={20} />
        </div>
      </div>
    </div>
  )
}

export default QuestsPage