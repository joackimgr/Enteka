import axios from 'axios';

const personalIp = import.meta.env.VITE_PERSONAL_IP || 'localhost';
const BASE_URL = `http://${personalIp}:8000`;
export const API_BASE = BASE_URL;
export const WS_BASE = `ws://${personalIp}:8000`;

export const loginDataPython = async (data) => {
    try {
        const response = await axios.post(`${BASE_URL}/login`, {
            username: data.username,
            password: data.password
        });
        return response.data
    } catch (error) {
        console.error('Error sending data:', error);
        if (error.response?.data) return error.response.data;
        return { auth: false, message: 'Network error. Try again.' }
    }
}

export const signUpDataPython = async (data) => {
    try {
        const response = await axios.post(`${BASE_URL}/signup`, {
            username: data.username,
            email: data.email,
            password: data.password
        });
        return response.data
    } catch (error) {
        console.error('Error sending data:', error);
        if (error.response?.data) return error.response.data;
        return { auth: false, message: 'Network error. Try again.' }
    }
}

export const verifyToken = async (token) => {
    try {
        const response = await axios.post(`${BASE_URL}/verify`, {
            token: token
        })
        return response.data
    } catch (error) {
        console.error('Error verifying token', error)
        if (error.response?.data) return error.response.data;
        return {auth: false, message: 'Network error. Try again.'}
    }
}

export const search = async (query) => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.get(`${BASE_URL}/users/search?query=${query}`,
            { headers: { Authorization: `Bearer ${token}` } }
        )
        return response.data
    } catch(error) {
        console.error("Error searching user", error)
        return null
    }
}

export const searchFriends = async (query) => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.get(`${BASE_URL}/friends/search?query=${query}`, 
            { headers: { Authorization: `Bearer ${token}` } }
        )
        return response.data
    } catch (error) {
        console.error("Error searching friend", error)
        return null
    }
}

export const createChat = async (user2Id) => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.post(`${BASE_URL}/chats`,
            { user2_id: user2Id },
            { headers: { Authorization: `Bearer ${token}` }}
        )
        return response.data
    } catch (error) {
        console.error("Error creating chat", error)
        if (error.response?.data) return error.response.data;
        return null
    }
}

export const sendMessages = async (chatId, content) => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.post(`${BASE_URL}/messages`,
            { chat_id: chatId, content: content},
            { headers: { Authorization: `Bearer ${token}` }}
        )
        return response.data
    } catch (error) {
        console.error("Error sending message", error)
        return null
    }
}

export const getMessages = async (chatId) => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.get(`${BASE_URL}/messages/${chatId}`, {
            headers: { Authorization: `Bearer ${token}` }
        })
        return response.data
    } catch (error) {
        console.error("Error searching messages", error)
        return null
    }
}

export const getChats = async () => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.get(`${BASE_URL}/chats`, {
            headers: { Authorization: `Bearer ${token}` }
        })
        return response.data
    } catch (error) {
        console.error("Error searching chat", error)
        return null
    }
}

export const getFriendsList = async () => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.get(`${BASE_URL}/friends`, {
            headers: { Authorization: `Bearer ${token}` }
        })
        return response.data
    } catch (error) {
        console.error("Error searching friends", error)
    }
}

export const getFriendRequests = async () => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.get(`${BASE_URL}/friends/requests`, {
            headers: { Authorization: `Bearer ${token}` }
        })
        return response.data
    } catch (error) {
        console.error("Error getting friend requests", error)
    }
}

export const sendFriendRequest = async (user_id) => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.post(`${BASE_URL}/friends/request/${user_id}`, 
            { user2_id: user_id }, 
            { headers: { Authorization: `Bearer ${token}` }
        })
        console.log("Friend Request has been sent")
        return response.data
    } catch (error) {
        console.error("Error sending request", error)
        if(error.response?.data) return error.response.data;
        return { auth: false, message: "Network error. Try again."}
    }
}

export const acceptFriendRequest = async (request_id) => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.post(`${BASE_URL}/friends/accept/${request_id}`, {}, {
            headers: { Authorization: `Bearer ${token}` }
        })
        return response.data
    } catch (error) {
        console.error("Error accepting friend request", error)
    }
}

export const rejectFriendRequest = async (request_id) => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.post(`${BASE_URL}/friends/reject/${request_id}`, {}, {
            headers: { Authorization: `Bearer ${token}`}
        })
        return response.data
    } catch (error) {
        console.error("Error rejecting friend request", error)
    }
}

export const deleteFriend = async (friend_id) => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.delete(`${BASE_URL}/friends/${friend_id}`, {
            headers: { Authorization: `Bearer ${token}` }
        })
        return response.data
    } catch (error) {
        console.error("Error deleting friend", error)
    }
}

export const getMe = async () => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.get(`${BASE_URL}/users/me`, {
            headers: { Authorization: `Bearer ${token}` }
        })
        return response.data
    } catch (error) {
        console.error("Error getting user's info", error)
        if (error.response?.data) return error.response.data
        return null
    }
}

export const updateUsername = async (username) => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.put(`${BASE_URL}/users/me/username`, { username }, {
            headers: { Authorization: `Bearer ${token}`}
        })
        return response.data
    } catch (error) {
        console.error("Error updating username", error)
        if (error.response?.data) return error.response.data;
        return null
    }
}

export const updateEmail = async (email) => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.put(`${BASE_URL}/users/me/email`, { email }, {
            headers: { Authorization: `Bearer ${token}` }
        })
        return response.data
    } catch (error) {
        console.error("Error updating email", error)
        if (error.response?.data) return error.response.data
        return null
    }
}

export const updatePassword = async (current_password, new_password) => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.put(`${BASE_URL}/users/me/password`, { current_password, new_password }, {
            headers: { Authorization: `Bearer ${token}` }
        })
        return response.data
    } catch (error) {
        console.error("Error updating password", error)
        if (error.response?.data) return error.response.data
        return null
    }
}

export const updateProfilePic = async (image_url) => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.put(`${BASE_URL}/users/me/profile-picture`, { image_url }, {
            headers: { Authorization: `Bearer ${token}` }
        })
        return response.data
    } catch (error) {
        console.error("Error updating profile picture", error)
        if (error.response?.data) return error.response.data
        return null
    }
}