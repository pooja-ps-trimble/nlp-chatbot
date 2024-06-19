export const fetchResponse = async (chat) => {
    try {
        // after depoloyment you should change the fetch URL below
        console.log(chat[chat.length-1].message);
        const response = await fetch(`http://127.0.0.1:8000/qaWithBot/${chat[chat.length-1].message}`, {
            method: 'GET',
            headers: {
                "Content-Type": "application/json"
            }
        })

        const data = await response.json()
        console.log(data)
        return data
    } catch (error) {
        console.log(error);
    }
}

async function postData() {
    const url = 'http://127.0.0.1:8000/geturlsummary/';
    const data = { url: "https://example.com" };

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const jsonResponse = await response.json();
        console.log('Response:', jsonResponse);
    } catch (error) {
        console.error('Error:', error);
    }
}