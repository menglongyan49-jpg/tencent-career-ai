import { Router } from 'express'

const router = Router()

// 获取用户档案
router.get('/:id', (req, res) => {
  // 模拟数据
  res.json({
    id: req.params.id,
    nickname: '小鹅',
    grade: 'junior',
    major: '计算机科学',
    university: '示例大学',
    interests: ['产品经理', '技术开发'],
    goals: ['进入大厂工作', '获得实习经验'],
  })
})

// 更新用户档案
router.put('/:id', (req, res) => {
  res.json({
    success: true,
    message: '档案更新成功',
    data: req.body,
  })
})

export default router