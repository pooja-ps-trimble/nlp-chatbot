import { useState } from "react";
import ChatBody from "./components/ChatBody";
import ChatInput from "./components/ChatInput";
import { useMutation } from "react-query";
import { deleteIndex, fetchResponse, postData } from "./api";
import './App.css'
function App() {
  const [chat, setChat] = useState([]);
  const [url, setUrl] = useState([]);
  const [preUrl,  setPreUrl] = useState("")
  const [isError,  serIsError] = useState(false)
  const [info,setInfo] = useState("Note*: Provide the urls comma seperated.")

  const mutation = useMutation({
    mutationFn: () => {
      return fetchResponse(chat);
    },
    onSuccess: (data) => {
      setChat((prev) => [
        ...prev,
        { sender: "ai", message: data },
      ])
    }
  });

  const sendMessage = async (message) => {
    await Promise.resolve(setChat((prev) => [...prev, message]));
    mutation.mutate();
  };

  function checkForURL(inputString) {
    var urlPattern = /(https?:\/\/[^\s]+)/g;
    return urlPattern.test(inputString);
  }

  const handleUrl = async ()=>{
    serIsError(false)
    mutation.isLoading = true
    const urlArr = preUrl.split(',')
    console.log("Clicked url",urlArr)
    var error = false;
    urlArr.map(ele=>{
      if(!checkForURL(ele)){
        error = true
        serIsError(true)
      }
    })
    if(!error){
      setUrl(urlArr);
      const summary = await postData(urlArr);
      if(summary){
        setChat(prv=>[...prv,{ sender: "ai", message: summary }])
      }
    }
    mutation.isLoading = false

  }

  const handleClear = async()=>{
    setPreUrl("");
    setUrl([]);
    setChat([])
    serIsError(false)
    const isDeleted  = await deleteIndex();
    if(isDeleted) setInfo("Deleted👍")
    else setInfo("Index Not created")
  }

  return (
    <div className="bg-[#1A232E] h-screen py-6 relative sm:px-16 px-12 text-white overflow-hidden flex flex-col justify-between  align-middle">
      {/* gradients */}
      {/* <div className="gradient-01 z-0 absolute"></div> */}
      <div className="gradient-02 z-0 absolute"></div>

      {/* header */}
      <div className="uppercase font-bold  text-2xl text-center mb-3">
        Trimble Assistant - Web Scraping
      </div>

      {/* body */}
      <div
        className="h-[90%] overflow-auto w-full max-w-4xl min-w-[20rem] py-8 px-4 self-center
      scrollbar-thumb-slate-400 scrollbar-thin scrollbar-track-gray-tranparent scrollbar-thumb-rounded-md
      "
      >
        <div className="get-url">
          <textarea type="text" style={{color:"black",borderRadius:"5px"}} className="border-0  outline-none w-11/12" value={preUrl} onChange={(e)=>setPreUrl(e.target.value)} name="url" />
          {isError &&<p id="msg" style={{color:"red"}}>Something wrong in the url</p>}
          <p>{info}</p>
          <br />
          <div className="action-items">
          <button type="button" onClick={handleUrl} disabled={url.length >0} className="en-btn" >Enter</button>
          <button type="button" onClick={handleClear} disabled={url.length <0} className="en-btn" >Clear</button>

          </div>
        </div>
        <ChatBody chat={chat} />
      </div>

      {/* input */}
      <div className="w-full max-w-4xl min-w-[20rem] self-center">
        <ChatInput sendMessage={sendMessage} loading={mutation.isLoading} />
      </div>
    </div>
  );
}

export default App;
