import { useEffect, useState } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import { getVideoDetail, deleteVideo, refreshVideoStats } from "../services/api";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer
} from "recharts";

const formatNumber = (num) => {
  if (num >= 1_000_000_000) return (num / 1_000_000_000).toFixed(1) + "B";
  if (num >= 1_000_000) return (num / 1_000_000).toFixed(1) + "M";
  if (num >= 1_000) return (num / 1_000).toFixed(1) + "K";
  return num;
};


export default function VideoDetail() {
  const { id } = useParams();
  const { state } = useLocation();
  const navigate = useNavigate();
  const [refreshing, setRefreshing] = useState(false);
  const [video, setVideo] = useState(null);
  const [ai, setAI] = useState({});
  const [statsHistory, setStatsHistory] = useState([]);
  const [dominantColor, setDominantColor] = useState("#121212");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await getVideoDetail(id);

        setVideo(res.video);
        setAI(res.ai_summary || {});
        setStatsHistory(res.history || []);

        if (res.video?.thumbnail_url) {
          extractColor(res.video.thumbnail_url);
        }
      } catch (err) {
        console.error(err);
        setError("Error loading video");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id]);

  const extractColor = (imageUrl) => {
    const img = new Image();
    img.crossOrigin = "Anonymous";
    img.src = imageUrl;

    img.onload = () => {
      const canvas = document.createElement("canvas");
      const ctx = canvas.getContext("2d");

      canvas.width = img.width;
      canvas.height = img.height;

      ctx.drawImage(img, 0, 0);

      const data = ctx.getImageData(0, 0, 1, 1).data;
      const color = `rgb(${data[0]}, ${data[1]}, ${data[2]})`;

      setDominantColor(color);
    };
  };

  /**          chart data                              */

  const chartData = [...statsHistory]
    .sort((a, b) => new Date(a.snapshot_at) - new Date(b.snapshot_at))
    .map(item => ({
      timestamp: new Date(item.snapshot_at).getTime(),
      views: item.views,
      likes: item.likes,
      comments: item.comments || 0
    }));

  /* ---------------- ACTIONS ---------------- */

  const handleRefreshStats = async () => {
    setRefreshing(true); 

    try {
      const res = await refreshVideoStats(video.id);

      setVideo(prev => ({
        ...prev,
        views: res.views,
        likes: res.likes,
        engagement_rate: res.engagement_rate
      }));

      setStatsHistory(prev => [res, ...prev]);

      setMessage("Stats refreshed successfully");
      setTimeout(() => setMessage(""), 3000);

    }catch (err) {
      console.error(err);
      setMessage("Error refreshing stats");
      setTimeout(() => setMessage(""), 3000);
    } finally {
      setRefreshing(false);
    }
  };

  const handleDelete = async () => {
    const confirmDelete = window.confirm(`Delete "${video.title}"?`);
    if (!confirmDelete) return;

    try {
      await deleteVideo(video.id);

      alert("Video deleted successfully");
      navigate(-1);

    } catch (err) {
      console.error(err);
      alert("Error deleting video");
    }
  };

  /* ---------------- STATES ---------------- */

  if (loading) {
    return <div className="p-10 text-white">Loading video...</div>;
  }

  if (error) {
    return <div className="p-10 text-red-500">{error}</div>;
  }

  if (!video) {
    return <div className="p-10 text-white">Video not found</div>;
  }

  return (
    <div className="min-h-screen text-white animate-fade-in">

      {/* TOAST MESSAGE */}
      {message && (
        <div className="fixed top-4 right-4 bg-green-600 px-4 py-2 rounded-lg shadow-lg z-50">
          {message}
        </div>
      )}

      {/* HEADER */}
      <div className="relative h-[300px] w-full overflow-hidden">

        {/* BUTTONS */}
        <div className="absolute top-4 right-6 z-20 flex gap-3">

          <button
            onClick={handleRefreshStats}
            disabled={refreshing}
            className={`px-4 py-2 rounded-lg font-semibold transition
            ${refreshing 
            ? "bg-gray-500 cursor-not-allowed" 
            : "bg-[#1DB954] text-black hover:scale-105"}
            `}
          >
          {refreshing ? "Refreshing..." : "Refresh"}
          </button>

          <button
            onClick={handleDelete}
            className="bg-red-600/80 backdrop-blur px-4 py-2 rounded-lg hover:scale-105 transition"
          >
            Delete
          </button>

        </div>

        {/* BACKGROUND */}
        <img
          src={video.thumbnail_url}
          alt="bg"
          className="absolute h-full w-full object-cover blur-2xl scale-125 opacity-40"
        />

        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[#121212]" />

        {/* TITLE */}
        <div className="relative z-10 flex flex-col items-center justify-center text-center px-6 pt-16">
          <h1 className="text-3xl md:text-4xl font-bold max-w-3xl leading-tight">
            {video.title}
          </h1>
        </div>

      </div>

      {/* THUMB */}
      <div className="flex justify-center -mt-16 relative z-20">
        <img
          src={video.thumbnail_url}
          alt={video.title}
          className="w-[420px] rounded-2xl shadow-2xl border border-[#2a2a2a]"
        />
      </div>

      {/* AI */}
      <div className="max-w-5xl mx-auto mt-12 px-6 space-y-8">

        <div>
          <h2 className="text-xl font-semibold mb-3 text-[#1DB954]">
            AI Summary
          </h2>
          <p className="text-secondary leading-relaxed">
            {ai.video_summary || "No summary available"}
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <Card title="Hook Analysis" value={ai.hook_analysis} />
          <Card title="Sentiment" value={ai.sentiment} />
          <Card title="Content Category" value={ai.content_category} />
          <Card title="Engagement Insight" value={ai.engagement_insight} />
        </div>

        {ai.main_topics?.length > 0 && (
          <div>
            <h3 className="text-[#1DB954] font-semibold mb-3">
              Main Topics
            </h3>

            <div className="flex flex-wrap gap-2">
              {ai.main_topics.map((topic, i) => (
                <span
                  key={i}
                  className="px-3 py-1 bg-[#1DB954] text-black rounded-full text-sm font-medium"
                >
                  {topic}
                </span>
              ))}
            </div>
          </div>
        )}

      </div>

      {/* STATS */}
      <div className="max-w-5xl mx-auto mt-12 px-6 grid grid-cols-3 gap-6">
        <Stat title="Views" value={video.views} />
        <Stat title="Likes" value={video.likes} />
        <Stat
          title="Engagement"
          value={
            video.engagement_rate
              ? `${video.engagement_rate.toFixed(2)}%`
              : "0%"
          }
        />
      </div>

      {/* HISTORY */}
      <div className="max-w-5xl mx-auto mt-16 px-6 pb-16">
        <h2 className="text-xl font-semibold mb-4 text-[#1DB954]">
          Performance Over Time
        </h2>

        <div className="p-6 bg-[#181818] border border-[#2a2a2a] rounded-2xl w-full">
          {statsHistory.length === 0 ? (
            <p className="text-secondary text-center">
              No historical data yet
            </p>
          ) : (
            <>
          {/* LISTA ORIGINAL */}
        <ul className="space-y-2 mb-8">
          {statsHistory.map((s, i) => (
        <li key={i} className="text-sm text-secondary">
          {new Date(s.snapshot_at).toLocaleDateString()} —{" "}
          {s.views.toLocaleString()} views
        </li>
          ))}
        </ul>

          {/* GRAFICAS ABAJO (correcto) */}
        <div className="mt-8 grid md:grid-cols-1 gap-8">
          <StatChart
            data={chartData}
            dataKey="likes"
            color="#22c55e"
            title="Likes Over Time"
          />

          <StatChart
            data={chartData}
            dataKey="comments"
            color="#f59e0b"
            title="Comments Over Time"
          />

          <StatChart
            data={chartData}
            dataKey="views"
            color="#3b82f6"
            title="Views Over Time"
          />
        </div>
        </>
          )}
        </div>
      </div>

    </div>
  );
}

/* ---------------- COMPONENTS ---------------- */

function Card({ title, value }) {
  return (
    <div className="channel-card p-5">
      <h3 className="text-[#1DB954] font-semibold mb-2">{title}</h3>
      <p className="text-secondary">{value || "N/A"}</p>
    </div>
  );
}

function Stat({ title, value }) {
  return (
    <div className="channel-card p-6 text-center">
      <p className="text-secondary">{title}</p>
      <h3 className="text-2xl font-bold">
        {typeof value === "number"
          ? value.toLocaleString()
          : value || 0}
      </h3>
    </div>
  );
}

function StatChart({ data, dataKey, color, title }) {
  return (
    <div className="w-full h-[400px] mb-10">
      <h3 className="text-white mb-4">{title}</h3>

      <div className="w-full h-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart 
            data={data}
            margin={{ top: 10, right: 30, left: 60, bottom: 30 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />

            <XAxis
              dataKey="timestamp"
              type="number"
              domain={['dataMin', 'dataMax']}
              tickFormatter={(value) => new Date(value).toLocaleDateString()}
            />

            <YAxis 
              tick={{ fill: "#aaa", fontSize: 12 }} 
              tickFormatter={formatNumber}
            />

            <Tooltip
              formatter={(value) => formatNumber(value)}
              contentStyle={{
                backgroundColor: "#121212",
                border: "1px solid #333",
                borderRadius: "10px"
              }}
            />

            <Line
              type="monotone"
              dataKey={dataKey}
              stroke={color}
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}