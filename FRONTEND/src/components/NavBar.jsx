import { useLocation, Link } from "react-router-dom";
import { Info } from "lucide-react";

export default function Navbar({ onAboutClick, isSpotify, setTheme }) {
  const location = useLocation();

  const links = [
    { name: "Home", path: "/" },
    { name: "Channels", path: "/channels" },
  ];

  return (
    <nav className={`fixed top-0 w-full z-50 shadow-lg ${
      isSpotify
        ? "navbar"
        : "backdrop-blur-md bg-slate-950 border-b border-slate-800"
    }`}>
      <div className="max-w-7xl mx-auto flex justify-between items-center px-6 py-4">

        <Link
          to="/"
          className={`text-lg font-semibold transition ${
            isSpotify
              ? "text-white hover:text-[#1DB954]"
              : "text-white hover:text-purple-400"
          }`}
        >
          YouTube Intelligence
        </Link>

        <div className="flex items-center gap-4">
        <button
          onClick={() =>
          setTheme(prev => prev === "spotify" ? "default" : "spotify")
          }
          className={`px-3 py-1 rounded-full transition ${
          isSpotify
          ? "btn-secondary text-white"
          : "bg-gray-700 hover:bg-gray-600 text-white"
          }`}
        >
          Switch UI
        </button>

          {links.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`px-3 py-1 rounded-full transition ${
                location.pathname === link.path
                  ? isSpotify
                    ? "btn-primary"
                    : "bg-purple-600 text-white"
                  : isSpotify
                    ? "text-secondary hover:bg-[#2a2a2a]"
                    : "text-slate-300 hover:bg-slate-800 hover:text-white"
              }`}
            >
              {link.name}
            </Link>
          ))}

          <button
            onClick={onAboutClick}
            className={`flex items-center gap-1 px-3 py-1 rounded-full transition ${
              isSpotify
                ? "btn-secondary text-white"
                : "bg-slate-800 hover:bg-purple-600 text-white"
            }`}
          >
            <Info size={16} /> About
          </button>

        </div>
      </div>
    </nav>
    
  );
}