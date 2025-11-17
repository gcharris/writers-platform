import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';

// Pages
import Home from './pages/Home';
import Browse from './pages/Browse';
import ViewWork from './pages/ViewWork';
import Upload from './pages/Upload';
import Login from './pages/Login';
import Register from './pages/Register';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 30000, // 30 seconds
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Home />} />
            <Route path="/browse" element={<Browse />} />
            <Route path="/works/:workId" element={<ViewWork />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Upload requires auth but no protected route component */}
            <Route path="/upload" element={<Upload />} />

            {/* Catch all */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
