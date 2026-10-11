import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ToastProvider } from './components/ui/Toast';
import Layout from './components/Layout';
import ProtectedRoute from './components/ProtectedRoute';

// Pages
import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import StudentDashboard from './pages/StudentDashboard';
import SubmitFeedback from './pages/SubmitFeedback';
import FeedbackExplorer from './pages/FeedbackExplorer';
import BooksPage from './pages/BooksPage';
import BookDetail from './pages/BookDetail';
import LibrarianDashboard from './pages/LibrarianDashboard';
import ModerationPage from './pages/ModerationPage';
import ReportsPage from './pages/ReportsPage';
import UserProfile from './pages/UserProfile';
import CommentOptimizer from './pages/CommentOptimizer';
import NotFoundPage from './pages/NotFoundPage';

function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/feedback" element={<FeedbackExplorer />} />
            <Route path="/books" element={<BooksPage />} />
            <Route path="/books/:id" element={<BookDetail />} />
            <Route path="/comment-optimizer" element={<CommentOptimizer />} />

            {/* Student Protected Routes */}
            <Route
              path="/student/dashboard"
              element={
                <ProtectedRoute allowedRoles={['student', 'librarian', 'admin']}>
                  <StudentDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/student/submit"
              element={
                <ProtectedRoute allowedRoles={['student', 'librarian', 'admin']}>
                  <SubmitFeedback />
                </ProtectedRoute>
              }
            />
            <Route
              path="/student/profile"
              element={
                <ProtectedRoute allowedRoles={['student', 'librarian', 'admin']}>
                  <UserProfile />
                </ProtectedRoute>
              }
            />

            {/* Librarian Protected Routes */}
            <Route
              path="/librarian/dashboard"
              element={
                <ProtectedRoute allowedRoles={['librarian', 'admin']}>
                  <LibrarianDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/librarian/moderation"
              element={
                <ProtectedRoute allowedRoles={['librarian', 'admin']}>
                  <ModerationPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/librarian/reports"
              element={
                <ProtectedRoute allowedRoles={['librarian', 'admin']}>
                  <ReportsPage />
                </ProtectedRoute>
              }
            />

            {/* Catch-all */}
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </Layout>
      </ToastProvider>
    </AuthProvider>
  );
}

export default App;
