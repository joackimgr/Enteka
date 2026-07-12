import axios from 'axios';

export const loginDataPython = async (data) => {
    try {
        const response = await axios.post('http://localhost:8000/login', {
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
        const response = await axios.post('http://localhost:8000/signup', {
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
        const response = await axios.post('http://localhost:8000/verify', {
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
        const response = await axios.get(`http://localhost:8000/users/search?query=${query}`)
        return response.data
    } catch(error) {
        console.error("Error searching user", error)
        return null
    }
}

export const createChat = async (user2Id) => {
    try {
        const token = localStorage.getItem("token")
        const response = await axios.post("http://localhost:8000/chats",
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
        const response = await axios.post("http://localhost:8000/messages",
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
        const response = await axios.get(`http://localhost:8000/messages/${chatId}`, {
            headers: {Authorization: `Bearer ${token}`}
        })
        return response.data
    } catch (error) {
        console.error("Error searching chat", error)
        return null
    }
}