import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { ChevronRight, ChevronLeft, Sparkles, GraduationCap, Heart, Target, Check } from 'lucide-react'
import { useUserStore } from '../store/userStore'
import GooseMascot from '../components/GooseMascot'

const GRADE_OPTIONS = [
  { value: 'freshman', label: '大一', desc: '刚入学，充满好奇' },
  { value: 'sophomore', label: '大二', desc: '开始思考专业方向' },
  { value: 'junior', label: '大三', desc: '准备实习探索' },
  { value: 'senior', label: '大四', desc: '正式求职阶段' },
  { value: 'graduate', label: '研究生', desc: '深造中，规划未来' },
]

const INTEREST_OPTIONS = [
  '产品经理', '技术开发', '数据分析', 'UI设计', '运营推广',
  '游戏策划', '市场营销', '人力资源', '投资分析', '内容创作',
]

const GOAL_OPTIONS = [
  '进入大厂工作', '获得实习经验', '提升专业技能', '了解行业动态',
  '明确职业方向', '准备求职面试', '拓展人脉资源', '探索创业机会',
]

const OnboardingPage: React.FC = () => {
  const navigate = useNavigate()
  const { setProfile } = useUserStore()
  const [step, setStep] = useState(0)
  const [formData, setFormData] = useState({
    nickname: '',
    grade: '',
    university: '',
    major: '',
    interests: [] as string[],
    goals: [] as string[],
  })

  const totalSteps = 4

  const handleNext = () => {
    if (step < totalSteps - 1) {
      setStep(step + 1)
    } else {
      // 完成引导
      setProfile({
        nickname: formData.nickname || '小鹅',
        grade: formData.grade as any,
        university: formData.university,
        major: formData.major,
        interests: formData.interests,
        goals: formData.goals,
      })
      navigate('/')
    }
  }

  const handleBack = () => {
    if (step > 0) {
      setStep(step - 1)
    }
  }

  const toggleArrayItem = (array: string[], item: string): string[] => {
    if (array.includes(item)) {
      return array.filter((i) => i !== item)
    }
    return [...array, item]
  }

  const canProceed = () => {
    switch (step) {
      case 0:
        return formData.nickname.length > 0
      case 1:
        return formData.grade.length > 0
      case 2:
        return formData.interests.length > 0
      case 3:
        return formData.goals.length > 0
      default:
        return true
    }
  }

  const renderStep = () => {
    switch (step) {
      case 0:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <Sparkles className="mx-auto mb-4 text-goose-yellow" size={40} />
              <h2 className="text-2xl font-bold mb-2">欢迎来到未来鹅！</h2>
              <p className="text-gray-500">让我们认识一下你</p>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  你的昵称
                </label>
                <input
                  type="text"
                  value={formData.nickname}
                  onChange={(e) => setFormData({ ...formData, nickname: e.target.value })}
                  placeholder="给自己起个可爱的名字"
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  学校（选填）
                </label>
                <input
                  type="text"
                  value={formData.university}
                  onChange={(e) => setFormData({ ...formData, university: e.target.value })}
                  placeholder="你的大学名称"
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  专业（选填）
                </label>
                <input
                  type="text"
                  value={formData.major}
                  onChange={(e) => setFormData({ ...formData, major: e.target.value })}
                  placeholder="你的专业方向"
                  className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 outline-none transition-all"
                />
              </div>
            </div>
          </div>
        )

      case 1:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <GraduationCap className="mx-auto mb-4 text-primary-500" size={40} />
              <h2 className="text-2xl font-bold mb-2">你现在是几年级？</h2>
              <p className="text-gray-500">不同阶段有不同的成长路径</p>
            </div>

            <div className="grid gap-3">
              {GRADE_OPTIONS.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setFormData({ ...formData, grade: option.value })}
                  className={`flex items-center justify-between p-4 rounded-xl border-2 transition-all ${
                    formData.grade === option.value
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-100 hover:border-gray-200'
                  }`}
                >
                  <div className="text-left">
                    <p className="font-medium">{option.label}</p>
                    <p className="text-sm text-gray-500">{option.desc}</p>
                  </div>
                  {formData.grade === option.value && (
                    <Check className="text-primary-500" size={20} />
                  )}
                </button>
              ))}
            </div>
          </div>
        )

      case 2:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <Heart className="mx-auto mb-4 text-pink-500" size={40} />
              <h2 className="text-2xl font-bold mb-2">你对哪些方向感兴趣？</h2>
              <p className="text-gray-500">选择1-3个感兴趣的领域</p>
            </div>

            <div className="flex flex-wrap gap-2">
              {INTEREST_OPTIONS.map((interest) => (
                <button
                  key={interest}
                  onClick={() =>
                    setFormData({
                      ...formData,
                      interests: toggleArrayItem(formData.interests, interest),
                    })
                  }
                  className={`px-4 py-2 rounded-full border-2 transition-all ${
                    formData.interests.includes(interest)
                      ? 'border-pink-500 bg-pink-50 text-pink-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  {interest}
                </button>
              ))}
            </div>

            {formData.interests.length > 0 && (
              <div className="bg-gray-50 rounded-xl p-4">
                <p className="text-sm text-gray-500 mb-2">已选择：</p>
                <div className="flex flex-wrap gap-2">
                  {formData.interests.map((i) => (
                    <span key={i} className="bg-primary-100 text-primary-700 px-3 py-1 rounded-full text-sm">
                      {i}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )

      case 3:
        return (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <Target className="mx-auto mb-4 text-green-500" size={40} />
              <h2 className="text-2xl font-bold mb-2">你希望达成什么目标？</h2>
              <p className="text-gray-500">选择1-3个目标，帮你规划路径</p>
            </div>

            <div className="grid grid-cols-2 gap-3">
              {GOAL_OPTIONS.map((goal) => (
                <button
                  key={goal}
                  onClick={() =>
                    setFormData({
                      ...formData,
                      goals: toggleArrayItem(formData.goals, goal),
                    })
                  }
                  className={`p-3 rounded-xl border-2 transition-all text-left ${
                    formData.goals.includes(goal)
                      ? 'border-green-500 bg-green-50 text-green-700'
                      : 'border-gray-100 hover:border-gray-200'
                  }`}
                >
                  <span className="text-sm">{goal}</span>
                </button>
              ))}
            </div>

            {formData.goals.length > 0 && (
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-4">
                <p className="text-sm text-gray-500 mb-2">你的目标：</p>
                <div className="flex flex-wrap gap-2">
                  {formData.goals.map((g) => (
                    <span key={g} className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm">
                      {g}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col">
      {/* 顶部进度条 */}
      <div className="p-4">
        <div className="max-w-md mx-auto">
          <div className="flex items-center gap-2 mb-2">
            <GooseMascot size={32} animate={false} />
            <span className="font-bold gradient-text">未来鹅</span>
          </div>
          <div className="flex gap-1">
            {Array.from({ length: totalSteps }).map((_, i) => (
              <div
                key={i}
                className={`flex-1 h-1.5 rounded-full transition-colors ${
                  i <= step ? 'bg-primary-500' : 'bg-gray-200'
                }`}
              />
            ))}
          </div>
          <p className="text-xs text-gray-400 mt-1">
            步骤 {step + 1} / {totalSteps}
          </p>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <AnimatePresence mode="wait">
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              {renderStep()}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>

      {/* 底部按钮 */}
      <div className="p-4 bg-white/80 backdrop-blur-sm border-t border-gray-100">
        <div className="max-w-md mx-auto flex gap-3">
          {step > 0 && (
            <button
              onClick={handleBack}
              className="flex items-center justify-center gap-1 px-6 py-3 rounded-xl border border-gray-200 hover:bg-gray-50 transition-colors"
            >
              <ChevronLeft size={18} />
              上一步
            </button>
          )}
          <button
            onClick={handleNext}
            disabled={!canProceed()}
            className="flex-1 flex items-center justify-center gap-1 px-6 py-3 rounded-xl bg-primary-500 text-white hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {step === totalSteps - 1 ? (
              <>
                开始探索
                <Sparkles size={18} />
              </>
            ) : (
              <>
                下一步
                <ChevronRight size={18} />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  )
}

export default OnboardingPage