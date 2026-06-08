import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Home,
  MessageCircle,
  User,
  Compass,
  Map,
  Briefcase,
  Target,
  Menu,
  X,
} from 'lucide-react'
import { useUserStore } from '../store/userStore'
import GooseMascot from './GooseMascot'

interface LayoutProps {
  children: React.ReactNode
}

const navItems = [
  { path: '/', icon: Home, label: '首页' },
  { path: '/chat', icon: MessageCircle, label: '对话' },
  { path: '/explorer', icon: Compass, label: '探秘' },
  { path: '/path', icon: Map, label: '路径' },
  { path: '/jobs', icon: Briefcase, label: '求职' },
  { path: '/quests', icon: Target, label: '任务' },
  { path: '/profile', icon: User, label: '我的' },
]

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation()
  const { profile, level, totalPoints } = useUserStore()
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen flex flex-col lg:flex-row">
      {/* 移动端顶部栏 */}
      <div className="lg:hidden fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-sm border-b border-gray-100 px-4 py-3 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <GooseMascot size={32} />
          <span className="font-bold text-lg gradient-text">未来鹅</span>
        </Link>

        <div className="flex items-center gap-3">
          {profile && (
            <div className="flex items-center gap-2 text-sm">
              <span className="bg-goose-yellow/20 text-amber-700 px-2 py-0.5 rounded-full text-xs font-medium">
                Lv.{level}
              </span>
              <span className="text-gray-500">{totalPoints} 积分</span>
            </div>
          )}
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </div>

      {/* 移动端菜单 */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="lg:hidden fixed top-16 left-0 right-0 z-40 bg-white/95 backdrop-blur-sm border-b border-gray-100 shadow-lg"
          >
            <nav className="p-4">
              <div className="grid grid-cols-4 gap-2">
                {navItems.map((item) => {
                  const isActive = location.pathname === item.path
                  return (
                    <Link
                      key={item.path}
                      to={item.path}
                      onClick={() => setIsMobileMenuOpen(false)}
                      className={`flex flex-col items-center gap-1 p-3 rounded-xl transition-all ${
                        isActive
                          ? 'bg-primary-500 text-white'
                          : 'hover:bg-gray-100 text-gray-600'
                      }`}
                    >
                      <item.icon size={20} />
                      <span className="text-xs">{item.label}</span>
                    </Link>
                  )
                })}
              </div>
            </nav>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 桌面端侧边栏 */}
      <aside className="hidden lg:flex flex-col w-64 bg-white/80 backdrop-blur-sm border-r border-gray-100 fixed left-0 top-0 bottom-0 z-40">
        {/* Logo */}
        <div className="p-6 border-b border-gray-100">
          <Link to="/" className="flex items-center gap-3">
            <GooseMascot size={40} />
            <div>
              <h1 className="font-bold text-xl gradient-text">未来鹅</h1>
              <p className="text-xs text-gray-400">职业成长AI陪伴体</p>
            </div>
          </Link>
        </div>

        {/* 用户信息卡片 */}
        {profile && (
          <div className="p-4">
            <div className="bg-gradient-to-br from-primary-50 to-blue-50 rounded-xl p-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-goose-yellow to-goose-orange flex items-center justify-center text-white font-bold">
                  {profile.nickname?.[0] || '鹅'}
                </div>
                <div>
                  <p className="font-medium text-gray-800">{profile.nickname}</p>
                  <p className="text-xs text-gray-500">{profile.major}</p>
                </div>
              </div>
              <div className="flex items-center justify-between text-sm">
                <span className="bg-goose-yellow/30 text-amber-700 px-2 py-0.5 rounded-full text-xs font-medium">
                  Lv.{level} 小鹅
                </span>
                <span className="text-gray-500">{totalPoints} 积分</span>
              </div>
            </div>
          </div>
        )}

        {/* 导航菜单 */}
        <nav className="flex-1 p-4 space-y-1">
          {navItems.map((item) => {
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                  isActive
                    ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30'
                    : 'hover:bg-gray-100 text-gray-600'
                }`}
              >
                <item.icon size={20} />
                <span className="font-medium">{item.label}</span>
              </Link>
            )
          })}
        </nav>

        {/* 底部信息 */}
        <div className="p-4 border-t border-gray-100">
          <p className="text-xs text-gray-400 text-center">
            陪伴每一只小鹅<br />飞向更远的未来
          </p>
        </div>
      </aside>

      {/* 主内容区 */}
      <main className="flex-1 lg:ml-64 pt-16 lg:pt-0">
        <div className="min-h-screen">
          {children}
        </div>
      </main>
    </div>
  )
}

export default Layout