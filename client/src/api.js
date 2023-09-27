export const fetchResponse = async (chat) => {
    try {
        // after depoloyment you should change the fetch URL below
        console.log(chat[0].message);
        const response = await fetch('http://127.0.0.1:8000/generate_text', {
            method: 'POST',
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text: chat[0].message
            })
        })

        const data = await response.json()
        return data
    } catch (error) {
        console.log(error);
    }
}
