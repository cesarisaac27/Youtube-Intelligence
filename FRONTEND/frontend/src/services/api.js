const API_URL = "http://127.0.0.1:8000"

/* ---------------- CHANNELS ---------------- */

export const getAllChannels = async () => {
  const response = await fetch(`${API_URL}/channels`)
  return response.json()
}

export const searchChannelByName = async (name) => {
  const response = await fetch(`${API_URL}/channels/search/${name}`)
  return response.json()
}

export const searchChannelByUser = async (user) => {
  const response = await fetch(`${API_URL}/channels/searchUser/${user}`)
  return response.json()
}

export const deleteChannel = async (channel_id) => {
  const response = await fetch(
    `${API_URL}/channels/deleteChannel/${channel_id}`,
    {
      method: "DELETE"
    }
  );

  if (!response.ok) {
    throw new Error("Failed to delete channel");
  }

  return response.json();
};

export const getChannelAnalysis = async (channelId) => {
  const response = await fetch(
    `${API_URL}/channels/${channelId}/existing_analysis`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch channel analysis");
  }

  return response.json();
};

/* ---------------- VIDEOS (CHANNEL LEVEL) ---------------- */

export const fetchVideos = async (channelId) => {
  const response = await fetch(
    `${API_URL}/videos/${channelId}/top`,
    {
      method: "POST",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch channel videos");
  }

  return response.json();
};

export const getChannelVideos = async (channelId) => {
  const response = await fetch(
    `${API_URL}/videos/channel/${channelId}`
  );

  if (response.status === 404) {
    return { videos: [], total: 0 };
  }

  if (!response.ok) {
    throw new Error("Failed to fetch videos");
  }

  return response.json();
};

/* ---------------- VIDEO DETAIL ---------------- */


export const getVideoOverview = async (videoId) => {
  const response = await fetch(
    `${API_URL}/videos/id/${videoId}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch video overview");
  }

  return response.json();
};


export const getVideoStatsHistory = async (videoId) => {
  const response = await fetch(
    `${API_URL}/videos/${videoId}/fullStats`
  );

  if (response.status === 404) {
    return [];
  }

  if (!response.ok) {
    throw new Error("Failed to fetch video stats history");
  }

  return response.json();
};


export const getVideoAI = async (videoId) => {
  const response = await fetch(
    `${API_URL}/videos/${videoId}/retrieve-ai-analysis`
  );

  if (response.status === 404) {
    return {};
  }

  if (!response.ok) {
    throw new Error("Failed to fetch video AI analysis");
  }

  return response.json();
};

export const getVideoDetail = async (videoId) => {
  try {
    const [overview, stats, ai] = await Promise.all([
      getVideoOverview(videoId),
      getVideoStatsHistory(videoId),
      getVideoAI(videoId),
    ]);

    return {
      video: overview,
      history: stats,
      ai_summary: ai || {}
    };

  } catch (error) {
    throw new Error("Failed to fetch full video detail");
  }
};



export const deleteVideo = async (internalVideoId) => {
  const response = await fetch(
    `${API_URL}/videos/deleteVid/${internalVideoId}`,
    {
      method: "DELETE",
    }
  );

  if (!response.ok) {
    throw new Error("Failed to delete video");
  }

  return response.json();
};


export const refreshVideoStats = async (internalVideoId) => {
  const response = await fetch(
    `${API_URL}/videos/${internalVideoId}/refreshStats`,
    {
      method: "POST",
    }
  );

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to refresh stats");
  }

  return response.json();
};

export const refreshAllChannelStats = async (internalChannelId) => {
  const res = await fetch(
    `${API_URL}/videos/${internalChannelId}/refreshAllStats`,
    {
    method: "POST",
    });

    if (!res.ok) {
      throw new Error("Failed to refresh stats");
    }

    return res.json();
};


export const fetchVideoByUrl = async (videoURL) => {
  const response = await fetch(
    `${API_URL}/videos/fetchSingleVideo?videoURL=${encodeURIComponent(videoURL)}`,
    { method: "POST" }
  );

  if (!response.ok) throw new Error("Video not found");

  return await response.json();
};