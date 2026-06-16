import { useState, useRef, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { MoreVertical } from "lucide-react";
import { useAuth } from "../context/AuthContext";

export default function UserAccountBlock() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef(null);

  // Close menu on click outside
  useEffect(() => {
    function handleClickOutside(e) {
      if (menuRef.current && !menuRef.current.contains(e.target)) {
        setMenuOpen(false);
      }
    }
    if (menuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [menuOpen]);

  if (!user) return null;

  const initials = user.name
    ? user.name
        .split(" ")
        .map((n) => n[0])
        .join("")
        .toUpperCase()
        .slice(0, 2)
    : "??";

  function handleLogout() {
    setMenuOpen(false);
    logout();
    navigate("/login");
  }

  return (
    <div className="relative border-t border-[var(--border-light)]" ref={menuRef}>
      <button
        id="user-account-block"
        onClick={() => setMenuOpen((prev) => !prev)}
        className="w-full p-4 flex items-center gap-3 bg-[var(--background)] text-[var(--foreground)] cursor-pointer border-none hover:bg-[var(--muted)] transition-colors duration-100"
      >
        {/* Avatar */}
        <div
          className="w-9 h-9 bg-[var(--foreground)] text-[var(--background)] flex items-center justify-center shrink-0"
          style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: "11px" }}
        >
          {initials}
        </div>

        {/* Name + email */}
        <div className="flex-1 text-left min-w-0">
          <div
            className="text-sm font-bold truncate"
            style={{ fontFamily: '"Source Serif 4", Georgia, serif' }}
          >
            {user.name}
          </div>
          <div
            className="text-xs text-[var(--muted-foreground)] truncate"
            style={{ fontFamily: '"JetBrains Mono", monospace' }}
          >
            {user.email}
          </div>
        </div>

        {/* More icon */}
        <MoreVertical size={16} strokeWidth={1.5} className="shrink-0" />
      </button>

      {/* Dropdown menu */}
      {menuOpen && (
        <div className="absolute bottom-full left-0 w-full bg-[var(--background)] border border-[var(--border-light)] z-50">
          <button
            disabled
            className="w-full text-left px-4 py-3 text-sm text-[var(--border-light)] cursor-not-allowed border-none bg-transparent"
            style={{ fontFamily: '"JetBrains Mono", monospace' }}
          >
            Account Settings
          </button>
          <div className="h-px bg-[var(--border-light)]" />
          <button
            id="sign-out-button"
            onClick={handleLogout}
            className="w-full text-left px-4 py-3 text-sm cursor-pointer border-none bg-transparent text-[var(--foreground)] hover:bg-[var(--foreground)] hover:text-[var(--background)] transition-colors duration-100"
            style={{ fontFamily: '"JetBrains Mono", monospace' }}
          >
            Sign Out
          </button>
        </div>
      )}
    </div>
  );
}
