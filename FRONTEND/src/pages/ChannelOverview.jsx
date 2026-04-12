import { useEffect, useState } from "react";
import { useParams, useLocation } from "react-router-dom";
import { getChannelAnalysis, getAllChannels, deleteChannel, fetchVideos } from "../services/api";
import { useNavigate } from "react-router-dom";

export default function ChannelOverview() {

  const { id } = useParams();
  const { state } = useLocation();

  const [channel, setChannel] = useState(state || null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate(); 
  const [fetching, setFetching] = useState(false);
  

  /* ---------------- FETCH ---------------- */

  useEffect(() => {

    const fetchData = async () => {
      try {

        let currentChannel = state;

        if (!currentChannel) {
          const channels = await getAllChannels();
          currentChannel = channels.find(c => String(c.id) === id);

          if (!currentChannel) {
            setError("Channel not found");
            setLoading(false);
            return;
          }

          setChannel(currentChannel);
        }

        const ai = await getChannelAnalysis(id);
        setAnalysis(ai);

      } catch {
        setError("Error loading channel");
      } finally {
        setLoading(false);
      }
    };

    fetchData();

  }, [id]);

  /* ---------------- DELETE ---------------- */

  const handleDelete = async () => {
  if (!channel) return;

  const confirmDelete = window.confirm(`Delete ${channel.name}?`);
  if (!confirmDelete) return;

  try {
    const res = await deleteChannel(channel.id);

    setMessage(
      res?.message || `channel: ${channel.name} deleted successfully`
    );

    setTimeout(() => {
      navigate("/channels");
    }, 1200);

    setError("");

  } catch (err) {
    setError("Error deleting channel");
    
  }
};

  /* -------------- Fetch videos -----------------------*/
  const handleFetch = async () => {
  if (!channel) return;

  const confirmFetch = window.confirm(`Fetch videos for ${channel.name}?`);
  if (!confirmFetch) return;

  try {
    setFetching(true);

    await fetchVideos(channel.id);

    navigate(`/channels/${channel.id}/videos`, { state: channel });

  } catch (err) {
    setError("Error fetching channel videos");
  } finally {
    setFetching(false);
  }
};

  /* ---------------- SKELETON ---------------- */

  if (loading) {
    return (
      <div className="min-h-screen text-white animate-pulse">

        {/* HEADER */}
        <div className="h-[300px] w-full bg-[#181818]" />

        <div className="px-10 py-10 space-y-6">

          {/* AI */}
          <div className="h-40 bg-[#181818] rounded-xl" />

          {/* GRID */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="h-32 bg-[#181818] rounded-xl" />
            <div className="h-32 bg-[#181818] rounded-xl" />
            <div className="h-32 bg-[#181818] rounded-xl" />
            <div className="h-32 bg-[#181818] rounded-xl" />
          </div>

          {/* STATS */}
          <div className="h-32 bg-[#181818] rounded-xl" />

        </div>
      </div>
    );
  }

  if (error) return <div className="p-10 text-red-500">{error}</div>;
  if (!channel) return <div className="p-10 text-white">Channel not found</div>;

  /* ---------------- UI ---------------- */

  return (

    <div className="min-h-screen text-white animate-fade-in">

      {/* HEADER */}

      <div className="relative h-[300px] w-full overflow-hidden">

        {channel.thumbnail_url && (
          <img
            src={channel.thumbnail_url}
            alt="bg"
            className="absolute w-full h-full object-cover blur-2xl scale-125 opacity-40"
          />
        )}

        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[#121212]" />

        <div className="relative z-10 flex justify-between items-start px-10 pt-20">

          <div className="flex items-center gap-6">

            <img
              src={channel.thumbnail_url}
              alt={channel.name}
              className="w-36 h-36 rounded-full object-cover border-4 border-[#1DB954]"
            />

            <div>
              <h1 className="text-4xl font-bold flex items-center gap-3">

                {channel.name}

                {channel.handle && (
                  <span className="text-[#1DB954] text-lg">
                    {channel.handle.startsWith("@")
                      ? channel.handle
                      : `@${channel.handle}`}
                  </span>
                )}

              </h1>

              <p className="text-secondary mt-2">
                YouTube Channel Overview
              </p>
            </div>

          </div>

          {/* ACTIONS */}

          <div className="flex gap-3 items-center">

            <button
              onClick={handleDelete}
              className="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 transition font-medium"
            >
              Delete
            </button>

            <button 
              onClick={() => navigate(`/channels/${channel.id}/videos`, { state: channel })}
              className="px-4 py-2 rounded-lg bg-[#2a2a2a] hover:bg-[#3a3a3a] transition">
              Videos
            </button>

            <button
              onClick={handleFetch}
              disabled={fetching}
              className="px-4 py-2 rounded-lg bg-[#1DB954] text-black hover:bg-[#1ed760] transition font-semibold disabled:opacity-50"
            >
              {fetching ? "Fetching..." : "Fetch Videos"}
            </button>

          </div>

        </div>

      </div>

      {/* CONTENT */}

      <div className="page-bg py-10">
        <div className="max-w-7xl mx-auto px-6">

        {message && <div className="status success mb-6">{message}</div>}

        {/* AI OVERVIEW */}

        <div className="channel-card p-8 rounded-xl mb-10 w-full">

          <h2 className="text-2xl font-semibold mb-4 text-[#1DB954]">
            AI Overview
          </h2>

          <p className="text-secondary leading-relaxed">
            {analysis?.channel_summary || "No summary available"}
          </p>

        </div> {/* max-w */}
</div> {/* page-bg */}

        {/* GRID */}

        <div className="grid md:grid-cols-2 gap-6 mb-10 w-full">

          <div className="channel-card p-6 rounded-xl">
            <h3 className="text-[#1DB954] font-semibold mb-2">
              Creator Profile
            </h3>
            <p className="text-secondary">
              {analysis?.creator_profile || "N/A"}
            </p>
          </div>

          <div className="channel-card p-6 rounded-xl">
            <h3 className="text-[#1DB954] font-semibold mb-2">
              Target Audience
            </h3>
            <p className="text-secondary">
              {analysis?.target_audience || "N/A"}
            </p>
          </div>

          <div className="channel-card p-6 rounded-xl">
            <h3 className="text-[#1DB954] font-semibold mb-2">
              Content Style
            </h3>
            <p className="text-secondary">
              {analysis?.content_style || "N/A"}
            </p>
          </div>

          <div className="channel-card p-6 rounded-xl">
            <h3 className="text-[#1DB954] font-semibold mb-2">
              Main Topics
            </h3>
            <p className="text-secondary">
              {analysis?.main_topics?.join(", ") || "N/A"}
            </p>
          </div>

        </div>

        {/* STATS */}

        <div className="channel-card p-8 rounded-xl w-full">

          <h2 className="text-2xl font-semibold mb-6 text-[#1DB954]">
            Channel Stats
          </h2>

          <div className="grid grid-cols-3 text-center">

            <div>
              <div className="text-2xl font-bold text-[#1DB954]">
                {channel.subscribers?.toLocaleString() || "0"}
              </div>
              <div className="text-secondary">Subscribers</div>
            </div>

            <div>
              <div className="text-2xl font-bold text-[#1DB954]">
                {channel.videos?.toLocaleString() || "0"}
              </div>
              <div className="text-secondary">Videos</div>
            </div>

            <div>
              <div className="text-2xl font-bold text-[#1DB954]">
                {channel.views?.toLocaleString() || "0"}
              </div>
              <div className="text-secondary">Views</div>
            </div>

          </div>

        </div>

      </div>

    </div>
  );
}