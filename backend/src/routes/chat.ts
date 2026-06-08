import { Router } from 'express'
import { chatWithAI, getChatSuggestions } from '../services/chatService'

const router = Router()

// 对话接口
router.post('/', async (req, res, next) => {
  try {
    const { message, context } = req.body

    if (!message) {
      return res.status(400).json({ error: '消息不能为空' })
    }

    const response = await chatWithAI(message, context)
    res.json({ response })
  } catch (error) {
    next(error)
  }
})

// 获取推荐问题
router.get('/suggestions', (req, res) => {
  const suggestions = getChatSuggestions()
  res.json({ suggestions })
})

export default router