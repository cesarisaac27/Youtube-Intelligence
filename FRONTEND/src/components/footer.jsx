import { Heart } from "lucide-react";

export default function Footer() {
  return (
    <footer className="text-center mt-20 px-4 py-6 text-secondary">
      Built with
      <Heart
        size={25}
        className="inline mx-2 text-red-500 heart-beat cursor-pointer"
        fill="currentColor"
      />
      using React & FastAPI
    </footer>
  );
}