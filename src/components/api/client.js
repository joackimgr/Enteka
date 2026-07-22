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
        console.log('Data sent successfully:', response.data);
        return response.data
    } catch (error) {
        console.error('Error sending data:', error);
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
        console.log('Data sent successfully:', response.data);
        return response.data
    } catch (error) {
        console.error('Error sending data:', error);
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
        return {auth: false, message: 'Network error. Try again.'}
    }
}

export const search = async (query) => {
    try {
        const response = await axios.get(`${BASE_URL}/users/search?query=${query}`)
        return response.data
    } catch(error) {
        console.error("Error searching user", error)
        return null
    }
}

export const createChat = async (user2Id) => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.post(`${BASE_URL}/chats`,
            { user2_id: user2Id },
            { headers: {Authorization: `Bearer ${token}`}}
        )
        return response.data
    } catch (error) {
        console.error("Error searching user", error)
        return null
    }
}

export const sendMessages = async (chatId, content) => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.post(`${BASE_URL}/messages`,
            { chat_id: chatId, content: content},
            { headers: {Authorization: `Bearer ${token}`}}
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
            headers: {Authorization: `Bearer ${token}`}
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
            headers: {Authorization: `Bearer ${token}`}
        })
        return response.data
    } catch (error) {
        console.log("Error searching chat", error)
        return null
    }
}