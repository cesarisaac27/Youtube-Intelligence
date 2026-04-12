import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useState } from "react";

import Layout from "./components/layout";
import LayoutSpotify from "./components/layoutspotify";
import ChannelOverview from "./pages/ChannelOverview";
import Landing from "./pages/landing";
import Channels from "./pages/channels";
import ChannelVideos from "./pages/ChannelVideos";
import VideoDetail from "./pages/VideoDetails";

function App() {
  const [theme, setTheme] = useState("default"); // "spotify"

  const CurrentLayout =
    theme === "spotify" ? LayoutSpotify : Layout;

  return (
    <BrowserRouter>
      <Routes>

        <Route
          path="/"
          element={<CurrentLayout setTheme={setTheme} theme={theme} />}
        >
          <Route index element={<Landing />} />
          <Route path="channels" element={<Channels />} />
          <Route path="channel/:id" element={<ChannelOverview />} />
          <Route path="channels/:id/videos" element={<ChannelVideos />} />
          <Route path="videos/:id" element={<VideoDetail />} />
           <Route path="/video/:id" element={<VideoDetail />} />
        </Route>

      </Routes>
    </BrowserRouter>
  );
}

export default App;