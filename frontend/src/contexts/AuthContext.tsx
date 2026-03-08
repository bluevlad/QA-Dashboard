import React, { createContext, useContext, useState, useCallback, useMemo } from 'react';

interface AuthContextType {
  isAuthenticated: boolean;
  token: string | null;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  token: null,
  logout: () => {},
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('qa_token'));

  const logout = useCallback(() => {
    localStorage.removeItem('qa_token');
    setToken(null);
  }, []);

  const value = useMemo(
    () => ({
      isAuthenticated: !!token,
      token,
      logout,
    }),
    [token, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
