import { Outlet } from "react-router-dom";
import Navbar from "./NavBar";
import Footer from "./footer";
import { useState } from "react";

export default function Layout({setTheme}) {
  const [showAbout, setShowAbout] = useState(false);

  return (
    <div className="min-h-screen flex flex-col bg-green-800 text-white">

      <Navbar 
        onAboutClick={() => setShowAbout(true)} 
        setTheme={setTheme}
      />

      <main className="flex-1 pt-24">
        <Outlet />
      </main>

      <Footer />

      {/* ABOUT MODAL */}
      {showAbout && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
          <div className="bg-slate-900 border border-slate-700 p-8 rounded-xl max-w-lg text-center">
            <h2 className="text-2xl font-bold mb-4">About</h2>

            <p className="text-slate-300 mb-6">
              V1.0
              This platform analyzes YouTube channels using data analytics
              and AI models to discover trends, engagement metrics and
              high performing creators.
            </p>

            <button
              onClick={() => setShowAbout(false)}
              className="bg-purple-600 px-6 py-2 rounded-lg hover:bg-purple-700"
            >
              Close
            </button>
          </div>
        </div>
      )}

    </div>
  );
}