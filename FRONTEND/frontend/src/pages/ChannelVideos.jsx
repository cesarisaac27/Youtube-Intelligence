import { useEffect, useState } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import { getChannelVideos, getAllChannels, refreshAllChannelStats, deleteVideo } from "../services/api";

export default function ChannelVideos() {
  const { id } = useParams();
  const { state } = useLocation();
  const navigate = useNavigate();

  const [channel, setChannel] = useState(state || null);
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshing, setRefreshing] = useState(false);
  const [noVideos, setNoVideos] = useState(false);
  const [message, setMessage] = useState("");

  const [openMenuId, setOpenMenuId] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        let currentChannel = state;

        if (!currentChannel) {
          const channels = await getAllChannels();
          currentChannel = channels.find(c => String(c.id) === id);

          if (!currentChannel) {
            setError("Channel not found");
            return;
          }

          setChannel(currentChannel);
        }

        const res = await getChannelVideos(id);

        if (!res.videos || res.videos.length === 0) {
          setNoVideos(true);
          setVideos([]);
        } else {
          setVideos(res.videos);
          setNoVideos(false);
        }

      } catch (err) {
        setError("Error loading videos");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [id, state]);

  /* ---------------- ACTIONS ---------------- */

  const handleDelete = async (video) => {
    if (!video?.id) return;

    const confirmDelete = window.confirm(`Delete "${video.title}"?`);
    if (!confirmDelete) return;

    try {
      const res = await deleteVideo(video.id);

      setMessage(
        res?.message || `Video: "${video.title}" deleted successfully`
      );

      setVideos(prev => prev.filter(v => v.id !== video.id));
      setOpenMenuId(null);

    } catch (err) {
      console.error(err);
      alert("Error deleting video");
    }
  };

  const handleRefreshAll = async () => {
    setRefreshing(true);
    setMessage("");

    try {
      const stats = await refreshAllChannelStats(id);

      const updatedVideos = videos.map(video => {
        const stat = stats.find(s => s.video_id === video.id);
        return stat ? { ...video, ...stat } : video;
      });

      setVideos(updatedVideos);

      setMessage("All video stats refreshed successfully");

    } catch (err) {
      console.error(err);
      setMessage("Error refreshing stats");
    } finally {
      setRefreshing(false);
    }
  };

  /* ---------------- LOADING ---------------- */

  if (loading) {
    return <div className="p-10 text-white">Loading videos...</div>;
  }

  /* ---------------- ERROR ---------------- */

  if (error) {
    return <div className="p-10 text-red-500">{error}</div>;
  }

  /* ---------------- NO VIDEOS ---------------- */

  if (noVideos) {
    return (
      <div className="min-h-screen text-white animate-fade-in">

        <div className="relative h-[250px] w-full overflow-hidden">

          {channel?.thumbnail_url && (
            <img
              src={channel.thumbnail_url}
              alt="bg"
              className="absolute w-full h-full object-cover blur-2xl scale-125 opacity-40"
            />
          )}

          <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[#121212]" />

          <div className="relative z-10 flex items-center justify-between px-10 pt-16">

            <div className="flex items-center gap-6">
              <img
                src={channel?.thumbnail_url}
                alt={channel?.name}
                className="w-28 h-28 rounded-full border-4 border-[#1DB954]"
              />

              <div>
                <h1 className="text-3xl font-bold">{channel?.name}</h1>
                <p className="text-secondary">Top Videos</p>
              </div>
            </div>

            {/* BOTÓN AQUÍ TAMBIÉN */}
            <button
              onClick={handleRefreshAll}
              disabled={refreshing}
              className={`px-5 py-2 rounded-lg font-medium transition ${
                refreshing
                  ? "bg-gray-500 cursor-not-allowed"
                  : "bg-[#1DB954] hover:bg-[#17a74a]"
              }`}
            >
              {refreshing ? "Refreshing..." : "Refresh All Stats"}
            </button>

          </div>
        </div>

        <div className="page-bg py-20 text-center">
          <h2 className="text-2xl font-semibold text-[#1DB954] mb-4">
            No videos saved for this channel
          </h2>

          <p className="text-secondary">
            Click "Fetch Videos" to retrieve data from YouTube
          </p>
        </div>

      </div>
    );
  }

  /* ---------------- UI NORMAL ---------------- */

  return (
    <div className="min-h-screen text-white animate-fade-in">

      {/* HEADER */}
      <div className="relative h-[250px] w-full overflow-hidden">

        {message && (
          <div className="max-w-6xl mx-auto px-6 mt-4">
            <div className="bg-green-600/20 border border-green-500 text-green-400 px-4 py-3 rounded-lg">
              {message}
            </div>
          </div>
        )}

        {channel?.thumbnail_url && (
          <img
            src={channel.thumbnail_url}
            alt="bg"
            className="absolute w-full h-full object-cover blur-2xl scale-125 opacity-40"
          />
        )}

        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[#121212]" />

        <div className="relative z-10 flex items-center justify-between px-10 pt-16">

          {/* LEFT */}
          <div className="flex items-center gap-6">
            <img
              src={channel?.thumbnail_url}
              alt={channel?.name}
              className="w-28 h-28 rounded-full border-4 border-[#1DB954]"
            />

            <div>
              <h1 className="text-3xl font-bold">{channel?.name}</h1>
              <p className="text-secondary">Top Videos</p>
            </div>
          </div>

          {/* 🔥 AQUÍ ESTABA EL ERROR: FALTABA ESTE BOTÓN */}
          <button
            onClick={handleRefreshAll}
            disabled={refreshing}
            className={`px-5 py-2 rounded-lg font-medium transition ${
              refreshing
                ? "bg-gray-500 cursor-not-allowed"
                : "bg-[#1DB954] hover:bg-[#17a74a]"
            }`}
          >
            {refreshing ? "Refreshing stats..." : "Refresh All Stats"}
          </button>

        </div>
      </div>

      {/* VIDEOS */}
      <div className="page-bg py-10">
        <div className="max-w-6xl mx-auto px-6">

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">

            {videos.map((video) => (
              <div
                key={video.id}
                onClick={() =>
                  navigate(`/videos/${video.id}`, { state: video })
                }
                className="relative channel-card rounded-xl overflow-hidden hover:scale-[1.02] transition cursor-pointer"
              >

                <div
                  className="absolute top-2 right-2 z-20"
                  onClick={(e) => e.stopPropagation()}
                >
                  <button
                    onClick={() =>
                      setOpenMenuId(openMenuId === video.id ? null : video.id)
                    }
                    className="bg-black/60 hover:bg-black/80 px-2 py-1 rounded-md"
                  >
                    ⋮
                  </button>

                  {openMenuId === video.id && (
                    <div className="absolute right-0 mt-2 w-40 bg-[#1e1e1e] rounded-lg shadow-lg border border-[#2a2a2a]">

                      <button
                        onClick={() =>
                          navigate(`/videos/${video.id}`, { state: video })
                        }
                        className="block w-full text-left px-4 py-2 hover:bg-[#2a2a2a]"
                      >
                        Go to video
                      </button>

                      <button
                        onClick={() => handleDelete(video)}
                        className="block w-full text-left px-4 py-2 hover:bg-red-600 text-red-400"
                      >
                        Delete video
                      </button>

                    </div>
                  )}
                </div>

                <img
                  src={video.thumbnail_url}
                  alt={video.title}
                  className="w-full h-48 object-cover"
                />

                <div className="p-4 space-y-2">
                  <h3 className="font-semibold line-clamp-2">
                    {video.title}
                  </h3>

                  <p className="text-sm text-secondary">
                    {video.views?.toLocaleString()} views
                  </p>
                </div>

              </div>
            ))}

          </div>

        </div>
      </div>

    </div>
  );
}