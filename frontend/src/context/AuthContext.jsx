import { createContext, useContext, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const savedToken = localStorage.getItem("auth_token");
    const savedUser = localStorage.getItem("user");

    if (savedToken && savedUser) {
      setToken(savedToken);
      try {
        setUser(JSON.parse(savedUser));
      } catch {
        localStorage.removeItem("auth_token");
        localStorage.removeItem("user");
      }
    }
    setIsLoading(false);
  }, []);

  function login(email, password) {
    const mockUser = {
      name: "Pragyan Srivastava",
      email: email || "pragyan@example.com",
    };
    const mockToken = "mock_token";

    localStorage.setItem("auth_token", mockToken);
    localStorage.setItem("user", JSON.stringify(mockUser));
    setToken(mockToken);
    setUser(mockUser);
  }

  function signup(name, email, password) {
    const mockUser = {
      name: name || "Pragyan Srivastava",
      email: email || "pragyan@example.com",
    };
    const mockToken = "mock_token";

    localStorage.setItem("auth_token", mockToken);
    localStorage.setItem("user", JSON.stringify(mockUser));
    setToken(mockToken);
    setUser(mockUser);
  }

  function logout() {
    localStorage.removeItem("auth_token");
    localStorage.removeItem("user");
    setToken(null);
    setUser(null);
  }

  const isAuthenticated = !!token;

  return (
    <AuthContext.Provider
      value={{ user, token, isAuthenticated, isLoading, login, signup, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
