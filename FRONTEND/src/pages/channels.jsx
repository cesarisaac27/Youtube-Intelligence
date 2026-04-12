import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  getAllChannels,
  searchChannelByName,
  searchChannelByUser,
  deleteChannel,
  fetchVideoByUrl
} from "../services/api";

export default function Channels() {

  const navigate = useNavigate();

  const [channels, setChannels] = useState([]);
  const [search, setSearch] = useState("");
  const [mode, setMode] = useState("name");
  const [title, setTitle] = useState("Discover Channels");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [menuOpen, setMenuOpen] = useState(null);
  const [videoResult, setVideoResult] = useState(null);

  /* ---------------- SEARCH (UNIFICADO) ---------------- */

  const handleSearch = async () => {
    if (!search) return;

    try {

      /* VIDEO SEARCH */
      if (mode === "video") {
        const data = await fetchVideoByUrl(search);

        setVideoResult(data);
        setChannels([]);
        setTitle("Video Result");
        setMessage("Video found");
        setError("");
        return;
      }

      /*  CHANNEL SEARCH */
      let data;

      if (mode === "name") data = await searchChannelByName(search);
      if (mode === "user") data = await searchChannelByUser(search);

      const formattedChannel = {
        id: data.channel.id,
        channel_id: data.channel.channel_id,
        name: data.channel.name,
        thumbnail_url: data.channel.thumbnail_url,
        subscribers: data.metrics.subscribers,
        views: data.metrics.total_views,
        videos: data.metrics.total_videos
      };

      setChannels([formattedChannel]);
      setVideoResult(null);
      setTitle("Search Result");
      setMessage("Channel found");
      setError("");

    } catch {
      setError(mode === "video" ? "No video found" : "No channel found");
      setMessage("");
      setChannels([]);
      setVideoResult(null);
    }
  };

  /* ---------------- SAVED CHANNELS ---------------- */

  const handleSavedChannels = async () => {
    try {
      const data = await getAllChannels();

      const formatted = data.map((c) => ({
        id: c.id,
        channel_id: c.channel_id,
        name: c.name,
        thumbnail_url: c.thumbnail_url,
        subscribers: c.subscribers,
        views: c.total_views,
        videos: c.total_videos,
        handle: c.handle
      }));

      setChannels(formatted);
      setVideoResult(null);
      setTitle("My Channels");
      setMessage("Channels loaded");
      setError("");

    } catch {
      setError("Could not load channels");
      setChannels([]);
    }
  };

  /* ---------------- DELETE CHANNEL ---------------- */

  const handleDeleteChannel = async (channelId) => {
    const channel = channels.find(c => c.id === channelId);

    if (!window.confirm(`Delete ${channel?.name}?`)) return;

    try {
      const response = await deleteChannel(channelId);

      setMessage(response.message || `channel: ${channel?.name} - deleted successfully`);

      setChannels((prev) =>
        prev.filter((c) => c.id !== channelId)
      );

      setError("");
      setMenuOpen(null);

    } catch {
      setError("Error deleting channel");
      setMessage("");
    }
  };

  /* ---------------- UI ---------------- */

  return (
    <div className="page-bg p-10">

      <h1 className="text-4xl font-bold mb-2">{title}</h1>

      <p className="text-gray-400 mb-8">
        Search YouTube creators or manage your tracked channels
      </p>

      {message && <div className="status success">{message}</div>}
      {error && <div className="status error">{error}</div>}

      {/* SEARCH PANEL */}

      <div className="search-panel">

        <div className="search-row">

          <select
            value={mode}
            onChange={(e) => {
              setMode(e.target.value);
              setSearch("");
            }}
            className="input"
          >
            <option value="name">Channel Name</option>
            <option value="user">@User</option>
            <option value="video">Video URL</option> {/* 🔥 NUEVO */}
          </select>

          <input
            type="text"
            placeholder={
              mode === "video"
                ? "Paste YouTube video URL..."
                : "Search YouTube channel..."
            }
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input"
          />

          <button onClick={handleSearch} className="btn-search">
            Search
          </button>

        </div>

        <div className="my-channels-wrapper">
          <button onClick={handleSavedChannels} className="btn-my-channels">
            My Channels
          </button>
        </div>

      </div>

      {/* CHANNEL GRID */}

      {channels.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-4 gap-12 mt-10 justify-items-center">

          {channels.map((channel) => (
            <div
              key={channel.channel_id}
              className="channel-card"
              onClick={() => navigate(`/channel/${channel.id}`, { state: channel })}
            >

              <div
                className="card-menu"
                onClick={(e) => {
                  e.stopPropagation();
                  setMenuOpen(menuOpen === channel.channel_id ? null : channel.channel_id);
                }}
              >
                ⋮
              </div>

              {menuOpen === channel.channel_id && (
                <div className="menu-dropdown">
                  <div onClick={(e) => {
                    e.stopPropagation();
                    navigate(`/channel/${channel.id}`, { state: channel });
                  }}>
                    Open Channel
                  </div>

                  <div onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteChannel(channel.id);
                  }}>
                    Delete Channel
                  </div>
                </div>
              )}

              {channel.thumbnail_url && (
                <img
                  src={channel.thumbnail_url}
                  alt={channel.name}
                  className="channel-avatar"
                />
              )}

              <h2 className="channel-title">{channel.name}</h2>

              <div className="channel-stats">
                <div>
                  <div className="stat-number">{channel.subscribers?.toLocaleString()}</div>
                  <div>Subs</div>
                </div>

                <div>
                  <div className="stat-number">{channel.videos?.toLocaleString()}</div>
                  <div>Videos</div>
                </div>

                <div>
                  <div className="stat-number">{channel.views?.toLocaleString()}</div>
                  <div>Views</div>
                </div>
              </div>

            </div>
          ))}
        </div>
      )}

      {/* VIDEO RESULT */}

      {videoResult && (
        <div className="flex justify-center mt-10">
          <div
            className="channel-card cursor-pointer"
            onClick={() => navigate(`/video/${videoResult.id}`, { state: videoResult })}
          >

            <img
              src={videoResult.thumbnail_url}
              alt={videoResult.title}
              className="w-full rounded-lg"
            />

            <h2 className="channel-title mt-4">
              {videoResult.title}
            </h2>

            <div className="channel-stats mt-4">
              <div>
                <div className="stat-number">{videoResult.views?.toLocaleString()}</div>
                <div>Views</div>
              </div>

              <div>
                <div className="stat-number">{videoResult.likes?.toLocaleString()}</div>
                <div>Likes</div>
              </div>

              <div>
                <div className="stat-number">{videoResult.comments?.toLocaleString()}</div>
                <div>Comments</div>
              </div>
            </div>

          </div>
        </div>
      )}

    </div>
  );
}