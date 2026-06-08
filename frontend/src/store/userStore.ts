import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface UserProfile {
  id: string
  nickname: string
  avatar: string
  grade: 'freshman' | 'sophomore' | 'junior' | 'senior' | 'graduate'
  major: string
  university: string
  interests: string[]
  skills: string[]
  goals: string[]
  createdAt: Date
  updatedAt: Date
}

export interface GrowthRecord {
  id: string
  type: 'skill' | 'project' | 'certificate' | 'experience' | 'achievement'
  title: string
  description: string
  date: Date
  points: number
}

interface UserState {
  isOnboarded: boolean
  profile: UserProfile | null
  growthRecords: GrowthRecord[]
  totalPoints: number
  level: number

  // Actions
  setOnboarded: (value: boolean) => void
  setProfile: (profile: Partial<UserProfile>) => void
  addGrowthRecord: (record: Omit<GrowthRecord, 'id'>) => void
  addPoints: (points: number) => void
  reset: () => void
}

const GRADE_NAMES: Record<string, string> = {
  freshman: '大一',
  sophomore: '大二',
  junior: '大三',
  senior: '大四',
  graduate: '研究生',
}

export const getGradeName = (grade: string): string => GRADE_NAMES[grade] || grade

const calculateLevel = (points: number): number => {
  if (points < 100) return 1
  if (points < 300) return 2
  if (points < 600) return 3
  if (points < 1000) return 4
  if (points < 1500) return 5
  return Math.floor(points / 300) + 5
}

export const useUserStore = create<UserState>()(
  persist(
    (set, get) => ({
      isOnboarded: false,
      profile: null,
      growthRecords: [],
      totalPoints: 0,
      level: 1,

      setOnboarded: (value) => set({ isOnboarded: value }),

      setProfile: (profileData) => {
        const current = get().profile
        const newProfile = {
          ...current,
          ...profileData,
          updatedAt: new Date(),
        } as UserProfile

        // 如果是新用户，设置创建时间
        if (!current) {
          newProfile.id = crypto.randomUUID()
          newProfile.createdAt = new Date()
          newProfile.avatar = '/goose-avatar.svg'
        }

        set({ profile: newProfile, isOnboarded: true })
      },

      addGrowthRecord: (record) => {
        const newRecord: GrowthRecord = {
          ...record,
          id: crypto.randomUUID(),
        }
        set((state) => ({
          growthRecords: [...state.growthRecords, newRecord],
        }))
        get().addPoints(record.points)
      },

      addPoints: (points) => {
        set((state) => {
          const newTotal = state.totalPoints + points
          return {
            totalPoints: newTotal,
            level: calculateLevel(newTotal),
          }
        })
      },

      reset: () =>
        set({
          isOnboarded: false,
          profile: null,
          growthRecords: [],
          totalPoints: 0,
          level: 1,
        }),
    }),
    {
      name: 'future-goose-user',
    }
  )
)