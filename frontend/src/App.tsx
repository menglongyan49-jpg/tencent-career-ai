import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useUserStore } from './store/userStore'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import ChatPage from './pages/ChatPage'
import ProfilePage from './pages/ProfilePage'
import ExplorerPage from './pages/ExplorerPage'
import PathPage from './pages/PathPage'
import JobsPage from './pages/JobsPage'
import QuestsPage from './pages/QuestsPage'
import OnboardingPage from './pages/OnboardingPage'

function App() {
  const { isOnboarded } = useUserStore()

  return (
    <BrowserRouter>
      <Routes>
        {/* 入口引导 */}
        <Route
          path="/onboarding"
          element={
            isOnboarded ? <Navigate to="/" replace /> : <OnboardingPage />
          }
        />

        {/* 主应用 */}
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="explorer" element={<ExplorerPage />} />
          <Route path="path" element={<PathPage />} />
          <Route path="jobs" element={<JobsPage />} />
          <Route path="quests" element={<QuestsPage />} />
        </Route>

        {/* 默认重定向 */}
        <Route
          path="*"
          element={
            isOnboarded ? <Navigate to="/" replace /> : <Navigate to="/onboarding" replace />
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default App