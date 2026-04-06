import { BarChart3, Brain, Users } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="px-6">

      {/* HERO */}
      <section className="text-center mt-20">
        <h1 className="text-5xl font-bold mb-6">
          Discover <span className="text-[#1DB954]">YouTube Channels</span>
        </h1>

        <p className="text-secondary max-w-xl mx-auto mb-8">
          Analyze YouTube channels using data analytics and AI insights.
          Discover high performing creators, analyze historical metrics,
          and understand audience engagement.
        </p>

        <button
          onClick={() => navigate("/channels")}
          className="btn-primary px-6 py-3 rounded-xl transition"
        >
          Discover Channels
        </button>
      </section>

      {/* FEATURES */}
      <section className="max-w-6xl mx-auto mt-24">
        <h2 className="text-3xl font-bold text-center mb-12">
          What makes us different?
        </h2>

        <div className="grid md:grid-cols-3 gap-8">

          {/* CARD 1 */}
          <div className="channel-card p-8 rounded-xl transition transform hover:scale-105">
            <Brain className="text-[#1DB954] mb-4" size={32} />
            <h3 className="text-lg font-semibold mb-2">AI Channel Insights</h3>
            <p className="text-secondary">
              Generate AI powered insights about YouTube channels and understand what drives growth.
            </p>
          </div>

          {/* CARD 2 */}
          <div className="channel-card p-8 rounded-xl transition transform hover:scale-105">
            <BarChart3 className="text-[#1DB954] mb-4" size={32} />
            <h3 className="text-lg font-semibold mb-2">Historical Metrics</h3>
            <p className="text-secondary">
              Analyze historical performance metrics for videos and detect growth patterns.
            </p>
          </div>

          {/* CARD 3 */}
          <div className="channel-card p-8 rounded-xl transition transform hover:scale-105">
            <Users className="text-[#1DB954] mb-4" size={32} />
            <h3 className="text-lg font-semibold mb-2">Audience Analysis</h3>
            <p className="text-secondary">
              Understand audience behavior, engagement, and trending topics.
            </p>
          </div>

        </div>
      </section>

      {/* DASHBOARD PREVIEW */}
      <section className="mt-24 flex justify-center">
        <div className="channel-card p-8 rounded-xl w-[520px] transition transform hover:scale-105">
          <h3 className="font-semibold mb-6">Channel Metrics Preview</h3>

          <div className="space-y-3 text-secondary">
            <div className="flex justify-between">
              <span>Subscribers</span>
              <span className="text-[#1DB954] font-semibold">1.2M</span>
            </div>

            <div className="flex justify-between">
              <span>Average Views</span>
              <span className="text-[#1DB954] font-semibold">150k</span>
            </div>

            <div className="flex justify-between">
              <span>Engagement Rate</span>
              <span className="text-[#1DB954] font-semibold">8.4%</span>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
}