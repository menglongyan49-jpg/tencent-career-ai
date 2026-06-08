import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Compass,
  Building2,
  Users,
  Lightbulb,
  MapPin,
  ChevronRight,
  Play,
  BookOpen,
  MessageCircle,
  Star,
} from 'lucide-react'
import GooseMascot from '../components/GooseMascot'

const BUSINESS_AREAS = [
  {
    id: 'wx',
    name: '微信事业群',
    icon: '💬',
    desc: '连接人与人，连接人与服务',
    products: ['微信', '企业微信', '微信支付'],
    color: 'from-green-400 to-green-600',
  },
  {
    id: 'game',
    name: '游戏事业群',
    icon: '🎮',
    desc: '创造快乐，连接世界',
    products: ['王者荣耀', '和平精英', '英雄联盟手游'],
    color: 'from-purple-400 to-purple-600',
  },
  {
    id: 'cloud',
    name: '云与智慧产业事业群',
    icon: '☁️',
    desc: '助力产业数字化升级',
    products: ['腾讯云', '腾讯会议', '企业微信'],
    color: 'from-blue-400 to-blue-600',
  },
  {
    id: 'pcg',
    name: '平台与内容事业群',
    icon: '📺',
    desc: '连接用户与内容生态',
    products: ['QQ', '腾讯视频', '腾讯新闻'],
    color: 'from-orange-400 to-orange-600',
  },
  {
    id: 'tech',
    name: '技术工程事业群',
    icon: '⚙️',
    desc: '打造技术底座，驱动创新',
    products: ['AI Lab', '优图实验室', '安全平台'],
    color: 'from-cyan-400 to-cyan-600',
  },
  {
    id: 'sng',
    name: '社交网络事业群',
    icon: '👥',
    desc: '构建社交生态平台',
    products: ['QQ空间', '腾讯文档', '腾讯课堂'],
    color: 'from-pink-400 to-pink-600',
  },
]

const STORIES = [
  {
    id: 1,
    name: '小林',
    role: '产品经理',
    year: '入职3年',
    avatar: '👨‍💼',
    quote: '在腾讯，每个产品想法都有机会被认真对待。',
    tags: ['产品思维', '用户洞察', '团队协作'],
  },
  {
    id: 2,
    name: '小王',
    role: '后端开发',
    year: '入职2年',
    avatar: '👨‍💻',
    quote: '技术氛围很好，大佬们都很愿意分享经验。',
    tags: ['技术成长', '架构设计', '开源贡献'],
  },
  {
    id: 3,
    name: '小陈',
    role: '游戏策划',
    year: '入职4年',
    avatar: '👩‍🎨',
    quote: '从玩家到创作者，这是最棒的职业转变。',
    tags: ['游戏设计', '创意实现', '用户研究'],
  },
]

const CULTURE_POINTS = [
  { title: '用户为本', desc: '一切以用户价值为依归', icon: Users },
  { title: '科技向善', desc: '用技术解决社会问题', icon: Lightbulb },
  { title: '正直进取', desc: '做正确的事，持续进步', icon: Star },
  { title: '协作创造', desc: '团队合作，共创价值', icon: MessageCircle },
]

const ExplorerPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'business' | 'culture' | 'stories'>('business')
  const [selectedBusiness, setSelectedBusiness] = useState<string | null>(null)

  return (
    <div className="min-h-screen pb-20">
      {/* 头部 */}
      <div className="bg-gradient-to-br from-green-500 to-teal-600 text-white p-6">
        <div className="flex items-center gap-3 mb-4">
          <Compass size={24} />
          <h1 className="text-xl font-bold">鹅厂探秘</h1>
        </div>
        <p className="text-white/80">沉浸式了解腾讯业务、文化与员工故事</p>
      </div>

      {/* 标签切换 */}
      <div className="sticky top-16 lg:top-0 bg-white/90 backdrop-blur-sm border-b border-gray-100 z-10">
        <div className="flex">
          {[
            { key: 'business', label: '业务板块', icon: Building2 },
            { key: 'culture', label: '企业文化', icon: Lightbulb },
            { key: 'stories', label: '员工故事', icon: Users },
          ].map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex-1 flex items-center justify-center gap-2 py-3 text-sm font-medium transition-colors ${
                activeTab === tab.key
                  ? 'text-primary-600 border-b-2 border-primary-500'
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
          {activeTab === 'business' && (
            <motion.div
              key="business"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              <p className="text-gray-500 text-sm mb-4">
                腾讯有多个事业群，每个专注于不同的业务领域
              </p>

              <div className="grid gap-4">
                {BUSINESS_AREAS.map((area) => (
                  <motion.div
                    key={area.id}
                    layout
                    className={`bg-white rounded-2xl overflow-hidden shadow-sm border border-gray-100 ${
                      selectedBusiness === area.id ? 'ring-2 ring-primary-500' : ''
                    }`}
                  >
                    <button
                      onClick={() => setSelectedBusiness(selectedBusiness === area.id ? null : area.id)}
                      className="w-full p-4 text-left"
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${area.color} flex items-center justify-center text-2xl`}>
                          {area.icon}
                        </div>
                        <div className="flex-1">
                          <h3 className="font-bold">{area.name}</h3>
                          <p className="text-sm text-gray-500">{area.desc}</p>
                        </div>
                        <ChevronRight
                          size={20}
                          className={`text-gray-400 transition-transform ${
                            selectedBusiness === area.id ? 'rotate-90' : ''
                          }`}
                        />
                      </div>
                    </button>

                    {selectedBusiness === area.id && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="px-4 pb-4"
                      >
                        <div className="pt-4 border-t border-gray-100">
                          <p className="text-xs text-gray-400 mb-2">代表产品</p>
                          <div className="flex flex-wrap gap-2">
                            {area.products.map((product) => (
                              <span
                                key={product}
                                className="bg-gray-100 px-3 py-1 rounded-full text-sm"
                              >
                                {product}
                              </span>
                            ))}
                          </div>

                          <button className="mt-4 w-full flex items-center justify-center gap-2 bg-primary-50 text-primary-600 py-2 rounded-xl hover:bg-primary-100 transition-colors">
                            <Play size={16} />
                            了解更多
                          </button>
                        </div>
                      </motion.div>
                    )}
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}

          {activeTab === 'culture' && (
            <motion.div
              key="culture"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-6 text-center">
                <GooseMascot size={60} />
                <h2 className="text-xl font-bold mt-4 mb-2">腾讯文化价值观</h2>
                <p className="text-gray-500 text-sm">正直、进取、协作、创造</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {CULTURE_POINTS.map((point, index) => (
                  <motion.div
                    key={point.title}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="bg-white rounded-2xl p-4 text-center"
                  >
                    <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center mx-auto mb-3">
                      <point.icon className="text-primary-600" size={24} />
                    </div>
                    <h3 className="font-bold mb-1">{point.title}</h3>
                    <p className="text-xs text-gray-500">{point.desc}</p>
                  </motion.div>
                ))}
              </div>

              <div className="bg-white rounded-2xl p-5">
                <h3 className="font-bold mb-3 flex items-center gap-2">
                  <MapPin size={18} className="text-red-500" />
                  工作地点
                </h3>
                <div className="flex flex-wrap gap-2">
                  {['深圳总部', '北京', '上海', '广州', '成都', '武汉'].map((city) => (
                    <span
                      key={city}
                      className="bg-gray-100 px-3 py-1.5 rounded-full text-sm"
                    >
                      {city}
                    </span>
                  ))}
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'stories' && (
            <motion.div
              key="stories"
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="space-y-4"
            >
              <p className="text-gray-500 text-sm">
                听听在腾讯工作的学长学姐们怎么说
              </p>

              {STORIES.map((story, index) => (
                <motion.div
                  key={story.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white rounded-2xl p-5"
                >
                  <div className="flex items-start gap-4">
                    <div className="w-14 h-14 bg-gradient-to-br from-goose-yellow to-goose-orange rounded-xl flex items-center justify-center text-2xl flex-shrink-0">
                      {story.avatar}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-bold">{story.name}</span>
                        <span className="text-xs bg-primary-100 text-primary-700 px-2 py-0.5 rounded-full">
                          {story.role}
                        </span>
                      </div>
                      <p className="text-xs text-gray-400 mb-2">{story.year}</p>
                      <p className="text-gray-600 text-sm italic mb-3">"{story.quote}"</p>
                      <div className="flex flex-wrap gap-1">
                        {story.tags.map((tag) => (
                          <span
                            key={tag}
                            className="text-xs bg-gray-100 px-2 py-0.5 rounded"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}

              <button className="w-full bg-primary-50 text-primary-600 py-3 rounded-xl hover:bg-primary-100 transition-colors flex items-center justify-center gap-2">
                <MessageCircle size={18} />
                查看更多故事
              </button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}

export default ExplorerPage