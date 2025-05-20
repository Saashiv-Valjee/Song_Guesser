const CLIENT_ID = "35f60b24656248148ba9dcbcdca80b9f";
const CLIENT_SECRET = "beb4fe927fbe4a04ad88a99b82ddfbdb"; // You must replace this
const info = document.getElementById("info");
const player = document.getElementById("player");

async function getAccessToken() {
  const credentials = btoa(`${CLIENT_ID}:${CLIENT_SECRET}`);
  try {
    const res = await fetch("https://accounts.spotify.com/api/token", {
      method: "POST",
      headers: {
        Authorization: `Basic ${credentials}`,
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: "grant_type=client_credentials",
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error_description || "Token fetch failed");
    return data.access_token;
  } catch (err) {
    info.innerText = `Error getting token: ${err.message}`;
    throw err;
  }
}

async function getTrack(trackID, token) {
  try {
    const res = await fetch(`https://api.spotify.com/v1/tracks/${trackID}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.error.message || "Track fetch failed");
    return data;
  } catch (err) {
    info.innerText = `Error loading track: ${err.message}`;
    throw err;
  }
}

(async () => {
  const params = new URLSearchParams(window.location.search);
  const trackID = params.get("track");

  if (!trackID) {
    info.innerText = "No ?track= ID provided.";
    return;
  }

  try {
    const token = await getAccessToken();
    const track = await getTrack(trackID, token);

    info.innerText = `Now playing: ${track.name} by ${track.artists.map(a => a.name).join(", ")}`;

    if (!track.preview_url) {
      info.innerText += "\n⚠️ No preview available for this track.";
    } else {
      player.src = track.preview_url;
      player.play();
    }
  } catch (err) {
    console.error(err);
  }
})();
