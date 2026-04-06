const API_URL = "http://127.0.0.1:8000"

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