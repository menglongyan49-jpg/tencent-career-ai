import React, { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Trash2, Plus, Loader2, Sparkles } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { useChatStore } from '../store/chatStore'
import { useUserStore } from '../store/userStore'
import GooseMascot from '../components/GooseMascot'
import { chatWithAI } from '../services/api'

const quickQuestions = [
  '腾讯有哪些岗位适合我？',
  '如何准备产品经理面试？',
  '互联网行业的发展趋势是什么？',
  '大厂实习需要具备什么能力？',
]

const ChatPage: React.FC = () => {
  const {
    conversations,
    currentConversationId,
    createConversation,
    setCurrentConversation,
    addMessage,
    updateMessage,
    deleteConversation,
    getCurrentConversation,
  } = useChatStore()

  const { profile } = useUserStore()
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const currentConversation = getCurrentConversation()

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [currentConversation?.messages])

  useEffect(() => {
    if (!currentConversationId && conversations.length === 0) {
      createConversation()
    }
  }, [currentConversationId, conversations.length, createConversation])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')

    let convId = currentConversationId
    if (!convId) {
      convId = createConversation()
    }

    // 添加用户消息
    addMessage(convId, { role: 'user', content: userMessage })

    // 添加加载中的助手消息
    const loadingMsgId = crypto.randomUUID()
    addMessage(convId, { role: 'assistant', content: '', isLoading: true })
    setIsLoading(true)

    try {
      // 调用 AI API
      const response = await chatWithAI(userMessage, profile)

      // 更新消息内容
      const conversation = conversations.find(c => c.id === convId)
      if (conversation) {
        const lastMsg = conversation.messages[conversation.messages.length - 1]
        updateMessage(convId, lastMsg.id, response)
      }
    } catch (error) {
      console.error('Chat error:', error)
      const conversation = conversations.find(c => c.id === convId)
      if (conversation) {
        const lastMsg = conversation.messages[conversation.messages.length - 1]
        updateMessage(convId, lastMsg.id, '抱歉，我遇到了一些问题，请稍后再试。')
      }
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleQuickQuestion = (question: string) => {
    setInput(question)
    inputRef.current?.focus()
  }

  const handleNewChat = () => {
    createConversation()
  }

  return (
    <div className="flex flex-col h-screen lg:h-[calc(100vh-0px)]">
      {/* 顶部栏 */}
      <div className="flex items-center justify-between px-4 py-3 bg-white/80 backdrop-blur-sm border-b border-gray-100">
        <div className="flex items-center gap-2">
          <GooseMascot size={32} animate={false} />
          <div>
            <h1 className="font-bold">未来鹅助手</h1>
            <p className="text-xs text-gray-500">随时为你解答职业困惑</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleNewChat}
            className="flex items-center gap-1 px-3 py-1.5 text-sm bg-primary-50 text-primary-600 rounded-lg hover:bg-primary-100 transition-colors"
          >
            <Plus size={16} />
            新对话
          </button>
          {currentConversationId && (
            <button
              onClick={() => deleteConversation(currentConversationId)}
              className="p-1.5 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
            >
              <Trash2 size={16} />
            </button>
          )}
        </div>
      </div>

      {/* 消息区域 */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {currentConversation?.messages.map((message, index) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            {message.role === 'assistant' ? (
              <div className="w-8 h-8 rounded-full bg-goose-yellow/30 flex items-center justify-center flex-shrink-0">
                <GooseMascot size={24} animate={false} />
              </div>
            ) : (
              <div className="w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center text-white text-sm font-medium flex-shrink-0">
                {profile?.nickname?.[0] || '我'}
              </div>
            )}

            <div
              className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                message.role === 'user'
                  ? 'bg-primary-500 text-white'
                  : 'bg-white shadow-sm border border-gray-100'
              }`}
            >
              {message.isLoading ? (
                <div className="flex items-center gap-2 text-gray-400">
                  <Loader2 className="animate-spin" size={16} />
                  <span>思考中...</span>
                </div>
              ) : (
                <div className={message.role === 'user' ? '' : 'prose prose-sm max-w-none'}>
                  {message.role === 'assistant' ? (
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  ) : (
                    message.content
                  )}
                </div>
              )}
            </div>
          </motion.div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* 快捷问题 */}
      {(!currentConversation || currentConversation.messages.length <= 1) && (
        <div className="px-4 pb-2">
          <div className="flex flex-wrap gap-2">
            {quickQuestions.map((q) => (
              <button
                key={q}
                onClick={() => handleQuickQuestion(q)}
                className="flex items-center gap-1 px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
              >
                <Sparkles size={14} className="text-goose-yellow" />
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 输入区域 */}
      <div className="p-4 bg-white/80 backdrop-blur-sm border-t border-gray-100">
        <div className="flex items-end gap-2 max-w-3xl mx-auto">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="问我任何职业发展问题..."
              rows={1}
              className="w-full px-4 py-3 bg-gray-100 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-primary-500/50 pr-12"
              style={{ minHeight: '48px', maxHeight: '120px' }}
            />
          </div>
          <button
            onClick={handleSend}
            disabled={!input.trim() || isLoading}
            className="p-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send size={20} />
          </button>
        </div>
        <p className="text-xs text-gray-400 text-center mt-2">
          未来鹅会基于你的背景提供个性化建议
        </p>
      </div>
    </div>
  )
}

export default ChatPage