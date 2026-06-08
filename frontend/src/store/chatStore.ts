import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface Message {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: Date
  isLoading?: boolean
}

export interface Conversation {
  id: string
  title: string
  messages: Message[]
  createdAt: Date
  updatedAt: Date
}

interface ChatState {
  conversations: Conversation[]
  currentConversationId: string | null

  // Actions
  createConversation: () => string
  setCurrentConversation: (id: string) => void
  addMessage: (conversationId: string, message: Omit<Message, 'id' | 'timestamp'>) => void
  updateMessage: (conversationId: string, messageId: string, content: string) => void
  deleteConversation: (id: string) => void
  clearAll: () => void

  // Getters
  getCurrentConversation: () => Conversation | undefined
}

export const useChatStore = create<ChatState>()(
  persist(
    (set, get) => ({
      conversations: [],
      currentConversationId: null,

      createConversation: () => {
        const id = crypto.randomUUID()
        const newConversation: Conversation = {
          id,
          title: '新对话',
          messages: [
            {
              id: crypto.randomUUID(),
              role: 'assistant',
              content: '你好呀！我是未来鹅 🦆，很高兴认识你！\n\n我可以帮你：\n- 了解互联网行业和腾讯\n- 规划职业成长路径\n- 提升求职技能\n- 解答各种职业困惑\n\n有什么想聊的吗？',
              timestamp: new Date(),
            },
          ],
          createdAt: new Date(),
          updatedAt: new Date(),
        }

        set((state) => ({
          conversations: [newConversation, ...state.conversations],
          currentConversationId: id,
        }))

        return id
      },

      setCurrentConversation: (id) => set({ currentConversationId: id }),

      addMessage: (conversationId, messageData) => {
        const message: Message = {
          ...messageData,
          id: crypto.randomUUID(),
          timestamp: new Date(),
        }

        set((state) => ({
          conversations: state.conversations.map((conv) =>
            conv.id === conversationId
              ? {
                  ...conv,
                  messages: [...conv.messages, message],
                  updatedAt: new Date(),
                  title:
                    conv.messages.length === 1 && messageData.role === 'user'
                      ? messageData.content.slice(0, 20) + (messageData.content.length > 20 ? '...' : '')
                      : conv.title,
                }
              : conv
          ),
        }))
      },

      updateMessage: (conversationId, messageId, content) => {
        set((state) => ({
          conversations: state.conversations.map((conv) =>
            conv.id === conversationId
              ? {
                  ...conv,
                  messages: conv.messages.map((msg) =>
                    msg.id === messageId ? { ...msg, content, isLoading: false } : msg
                  ),
                }
              : conv
          ),
        }))
      },

      deleteConversation: (id) => {
        set((state) => {
          const newConversations = state.conversations.filter((c) => c.id !== id)
          const newCurrentId =
            state.currentConversationId === id
              ? newConversations[0]?.id || null
              : state.currentConversationId

          return {
            conversations: newConversations,
            currentConversationId: newCurrentId,
          }
        })
      },

      clearAll: () =>
        set({
          conversations: [],
          currentConversationId: null,
        }),

      getCurrentConversation: () => {
        const state = get()
        return state.conversations.find((c) => c.id === state.currentConversationId)
      },
    }),
    {
      name: 'future-goose-chat',
    }
  )
)