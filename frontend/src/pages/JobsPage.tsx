import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Briefcase,
  FileText,
  MessageCircle,
  Target,
  ChevronRight,
  Upload,
  Play,
  Star,
  Clock,
  CheckCircle,
  AlertCircle,
} from 'lucide-react'
import { useUserStore } from '../store/userStore'
import GooseMascot from '../components/GooseMascot'

const JOB_CATEGORIES = [
  { id: 'tech', name: '技术类', icon: '💻', count: 156 },
  { id: 'product', name: '产品类', icon: '📱', count: 89 },
  { id: 'design', name: '设计类', icon: '🎨', count: 45 },
  { id: 'operation', name: '运营类', icon: '📊', count: 67 },
  { id: 'game', name: '游戏类', icon: '🎮', count: 78 },
  { id: 'other', name: '其他', icon: '📌', count: 34 },
]

const INTERVIEW_TIPS = [
  '自我介绍控制在1-2分钟，突出与岗位相关的经历',
  '用STAR法则回答行为面试题',
  '准备2-3个有深度的问题问面试官',
  '提前了解目标岗位的业务和团队',
]

const JobsPage: React.FC = () => {
  const { profile } = useUserStore()
  const [activeTab, setActiveTab] = useState<'resume' | 'interview' | 'jobs'>('resume')
  const [resumeScore, setResumeScore] = useState<number | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)

  const handleAnalyzeResume = () => {
    setIsAnalyzing(true)
    setTimeout(() => {
      setResumeScore(78)
      setIsAnalyzing(false)
    }, 2000)
  }

  return (
    <div className="min-h-screen pb-20">
      {/* 头部 */}
      <div className="bg-gradient-to-br from-orange-500 to-red-500 text-white p-6">
        <div className="flex items-center gap-3 mb-4">
          <Briefcase size={24} />
          <h1 className="text-xl font-bold">求职助手</h1>
        </div>
        <p className="text-white/80">简历优化、模拟面试，提升求职成功率</p>
      </div>

      {/* 标签切换 */}
      <div className="sticky top-16 lg:top-0 bg-white/90 backdrop-blur-sm border-b border-gray-100 z-10">
        <div className="flex">
          {[
            { key: 'resume', label: '简历优化', icon: FileText },
            { key: 'interview', label: '模拟面试', icon: MessageCircle },
            { key: 'jobs', label: '岗位推荐', icon: Target },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? 'text-orange-600 border-b-2 border-orange-500'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <tab.icon size={16} />
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* 内容区 */}
      <div className="p-4">
        <AnimatePresence mode="wait">
          {activeTab === 'resume' && (
            <motion.div
              key="resume"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              {/* 简历上传区 */}
              <div className="bg-white rounded-2xl p-6 text-center">
                <div className="w-20 h-20 bg-orange-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <Upload size={32} className="text-orange-500" />
                </div>
                <h3 className="font-bold mb-2">上传你的简历</h3>
                <p className="text-sm text-gray-500 mb-4">
                  支持 PDF、Word 格式，AI 将为你分析优化建议
                </p>
                <button
                  onClick={handleAnalyzeResume}
                  disabled={isAnalyzing}
                  className="bg-orange-500 text-white px-6 py-2 rounded-xl hover:bg-orange-600 disabled:opacity-50 transition-colors"
                >
                  {isAnalyzing ? '分析中...' : '上传并分析'}
                </button>
              </div>

              {/* 分析结果 */}
              {resumeScore !== null && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-white rounded-2xl p-5"
                >
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="font-bold">简历评分</h3>
                    <div className="flex items-center gap-2">
                      <span className="text-3xl font-bold text-orange-500">{resumeScore}</span>
                      <span className="text-gray-400">/100</span>
                    </div>
                  </div>

                  <div className="h-3 bg-gray-100 rounded-full overflow-hidden mb-4">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${resumeScore}%` }}
                      transition={{ duration: 1 }}
                      className="h-full bg-gradient-to-r from-orange-400 to-red-500 rounded-full"
                    />
                  </div>

                  <div className="space-y-3">
                    <div className="flex items-start gap-3 p-3 bg-green-50 rounded-xl">
                      <CheckCircle className="text-green-500 flex-shrink-0 mt-0.5" size={16} />
                      <div>
                        <p className="text-sm font-medium text-green-700">优点</p>
                        <p className="text-xs text-green-600">项目经历描述清晰，有量化成果</p>
                      </div>
                    </div>
                    <div className="flex items-start gap-3 p-3 bg-yellow-50 rounded-xl">
                      <AlertCircle className="text-yellow-500 flex-shrink-0 mt-0.5" size={16} />
                      <div>
                        <p className="text-sm font-medium text-yellow-700">改进建议</p>
                        <p className="text-xs text-yellow-600">增加与目标岗位相关的技能关键词</p>
                      </div>
                    </div>
                  </div>

                  <button className="w-full mt-4 bg-orange-50 text-orange-600 py-2 rounded-xl hover:bg-orange-100 transition-colors flex items-center justify-center gap-2">
                    查看详细优化建议
                    <ChevronRight size={16} />
                  </button>
                </motion.div>
              )}
            </motion.div>
          )}

          {activeTab === 'interview' && (
            <motion.div
              key="interview"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              {/* 模拟面试入口 */}
              <div className="bg-gradient-to-br from-orange-500 to-red-500 rounded-2xl p-6 text-white">
                <div className="flex items-center gap-4">
                  <GooseMascot size={60} />
                  <div>
                    <h3 className="font-bold text-lg">AI 模拟面试</h3>
                    <p className="text-white/80 text-sm">根据目标岗位进行模拟练习</p>
                  </div>
                </div>
                <button className="w-full mt-4 bg-white text-orange-600 py-3 rounded-xl font-medium hover:bg-orange-50 transition-colors flex items-center justify-center gap-2">
                  <Play size={18} />
                  开始模拟面试
                </button>
              </div>

              {/* 面试技巧 */}
              <div className="bg-white rounded-2xl p-5">
                <h3 className="font-bold mb-3 flex items-center gap-2">
                  <Star className="text-orange-500" size={18} />
                  面试技巧
                </h3>
                <div className="space-y-2">
                  {INTERVIEW_TIPS.map((tip, index) => (
                    <div
                      key={index}
                      className="flex items-start gap-3 p-3 bg-gray-50 rounded-xl"
                    >
                      <div className="w-6 h-6 bg-orange-100 rounded-full flex items-center justify-center text-xs font-medium text-orange-600 flex-shrink-0">
                        {index + 1}
                      </div>
                      <p className="text-sm text-gray-600">{tip}</p>
                    </div>
                  ))}
                </div>
              </div>

              {/* 历史记录 */}
              <div className="bg-white rounded-2xl p-5">
                <h3 className="font-bold mb-3 flex items-center gap-2">
                  <Clock className="text-gray-400" size={18} />
                  练习记录
                </h3>
                <div className="text-center py-8">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <MessageCircle size={24} className="text-gray-400" />
                  </div>
                  <p className="text-gray-400 text-sm">还没有模拟面试记录</p>
                  <p className="text-gray-300 text-xs mt-1">开始第一次练习吧</p>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'jobs' && (
            <motion.div
              key="jobs"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              {/* 推荐提示 */}
              {profile && (
                <div className="bg-orange-50 rounded-xl p-4 flex items-center gap-3">
                  <Target className="text-orange-500" size={20} />
                  <p className="text-sm text-orange-700">
                    基于{profile.interests[0] || '你的兴趣'}为你推荐相关岗位
                  </p>
                </div>
              )}

              {/* 岗位分类 */}
              <div className="grid grid-cols-3 gap-3">
                {JOB_CATEGORIES.map((cat) => (
                  <button
                    key={cat.id}
                    className="bg-white rounded-xl p-4 text-center hover:shadow-md transition-shadow"
                  >
                    <div className="text-2xl mb-2">{cat.icon}</div>
                    <p className="text-sm font-medium">{cat.name}</p>
                    <p className="text-xs text-gray-400">{cat.count}个岗位</p>
                  </button>
                ))}
              </div>

              {/* 热门岗位 */}
              <div className="bg-white rounded-2xl p-5">
                <h3 className="font-bold mb-3">热门岗位</h3>
                <div className="space-y-3">
                  {[
                    { title: '产品经理实习生', dept: '微信事业群', location: '深圳' },
                    { title: '后端开发工程师', dept: '云与智慧产业事业群', location: '北京' },
                    { title: '游戏策划', dept: '游戏事业群', location: '深圳' },
                  ].map((job, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors cursor-pointer"
                    >
                      <div>
                        <p className="font-medium text-sm">{job.title}</p>
                        <p className="text-xs text-gray-400">{job.dept} · {job.location}</p>
                      </div>
                      <ChevronRight size={16} className="text-gray-400" />
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

export default JobsPage