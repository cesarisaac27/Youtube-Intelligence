import { Outlet } from "react-router-dom";
import Navbar from "./NavBar";
import Footer from "./footer";
import { useState } from "react";


export default function LayoutSpotify({setTheme}) {
  const [showAbout, setShowAbout] = useState(false);

  return (
    <div className="spotify-theme min-h-screen flex flex-col">

      <Navbar 
        onAboutClick={() => setShowAbout(true)} 
        isSpotify 
        setTheme={setTheme}
        />

      <main className="flex-1 pt-24 px-4">
        <Outlet />
      </main>

      <Footer />

      {showAbout && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
          <div className="modal p-8 rounded-xl max-w-lg text-center shadow-2xl">
            <h2 className="text-2xl font-bold mb-4">About</h2>

            <p className="text-secondary mb-6">
              V1.0 <br />
              This platform analyzes YouTube channels using data analytics
              and AI models to discover trends and high performing creators.
            </p>

            <button
              onClick={() => setShowAbout(false)}
              className="btn-primary px-6 py-2 rounded-lg transition"
            >
              Close
            </button>
          </div>
        </div>
      )}

    </div>
  );
}