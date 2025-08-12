import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';

// Layout Components
import Layout from './components/Layout/Layout';

// Page Components
import Dashboard from './pages/Dashboard';
import Players from './pages/Players';
import Teams from './pages/Teams';
import Fixtures from './pages/Fixtures';
import Recommendations from './pages/Recommendations';
import Statistics from './pages/Statistics';
import PlayerComparison from './pages/PlayerComparison';

// Context Providers
import { ThemeProvider } from './context/ThemeContext';
import { DataProvider } from './context/DataContext';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <DataProvider>
          <Router>
            <div className="App min-h-screen bg-dark-950 text-white">
              <Layout>
                <Routes>
                  <Route path="/" element={<Dashboard />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/players" element={<Players />} />
                  <Route path="/teams" element={<Teams />} />
                  <Route path="/fixtures" element={<Fixtures />} />
                  <Route path="/recommendations" element={<Recommendations />} />
                  <Route path="/statistics" element={<Statistics />} />
                  <Route path="/compare" element={<PlayerComparison />} />
                </Routes>
              </Layout>
              
              {/* Toast notifications */}
              <Toaster
                position="top-right"
                toastOptions={{
                  duration: 4000,
                  style: {
                    background: '#1e293b',
                    color: '#f1f5f9',
                    border: '1px solid #334155',
                  },
                  success: {
                    iconTheme: {
                      primary: '#22c55e',
                      secondary: '#f1f5f9',
                    },
                  },
                  error: {
                    iconTheme: {
                      primary: '#ef4444',
                      secondary: '#f1f5f9',
                    },
                  },
                }}
              />
            </div>
          </Router>
        </DataProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
