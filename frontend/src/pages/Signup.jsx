import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Signup() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const { signup } = useAuth();
  const navigate = useNavigate();

  function handleSubmit(e) {
    e.preventDefault();
    signup(name, email, password);
    navigate("/");
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--background)] px-4">
      <div className="w-full max-w-[400px]">
        <h1
          className="text-4xl font-bold tracking-tight"
          style={{ fontFamily: '"Playfair Display", Georgia, serif' }}
        >
          Create Account
        </h1>

        <div className="h-[4px] bg-[var(--foreground)] mt-4 mb-10" />

        <form onSubmit={handleSubmit} className="flex flex-col gap-0">
          <div className="mb-6">
            <input
              id="signup-name"
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Full name"
              className="w-full bg-transparent border-b-2 border-[var(--foreground)] py-3 text-base focus:outline-none"
              style={{ fontFamily: '"JetBrains Mono", monospace' }}
            />
          </div>

          <div className="mb-6">
            <input
              id="signup-email"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Email address"
              className="w-full bg-transparent border-b-2 border-[var(--foreground)] py-3 text-base focus:outline-none"
              style={{ fontFamily: '"JetBrains Mono", monospace' }}
            />
          </div>

          <div className="mb-8">
            <input
              id="signup-password"
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Password"
              className="w-full bg-transparent border-b-2 border-[var(--foreground)] py-3 text-base focus:outline-none"
              style={{ fontFamily: '"JetBrains Mono", monospace' }}
            />
          </div>

          <button
            id="signup-submit"
            type="submit"
            className="w-full bg-[var(--foreground)] text-[var(--background)] uppercase tracking-widest py-4 text-sm font-medium cursor-pointer transition-colors duration-100 hover:bg-[var(--background)] hover:text-[var(--foreground)] border-2 border-[var(--foreground)]"
            style={{ fontFamily: '"JetBrains Mono", monospace' }}
          >
            Create Account
          </button>
        </form>

        <p
          className="mt-6 text-sm text-[var(--muted-foreground)]"
          style={{ fontFamily: '"JetBrains Mono", monospace' }}
        >
          Already have an account?{" "}
          <Link
            to="/login"
            className="text-[var(--foreground)] no-underline hover:underline"
          >
            Sign in →
          </Link>
        </p>
      </div>
    </div>
  );
}
