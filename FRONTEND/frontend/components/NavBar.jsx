import { Info } from "lucide-react"

export default function Navbar({ onAboutClick }) {

  return (

    <header className="flex justify-between items-center px-10 py-6">

      <h1 className="text-lg font-semibold">
        YouTube Intelligence
      </h1>

      <button
        onClick={onAboutClick}
        className="flex items-center gap-2 bg-slate-800 hover:bg-purple-600 transition px-4 py-2 rounded-full text-sm"
      >
        <Info size={16}/>
        About
      </button>

    </header>

  )
}