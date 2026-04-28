import { Navigate } from 'react-router-dom';
import { authStore } from '../services/api';

export default function ProtectedRoute({ children }) {
  return authStore.token ? children : <Navigate to="/login" replace />;
}
