document.getElementById("askBtn").addEventListener("click", () => {
    document.getElementById("answer").innerHTML ="Please wait , while we load your answer";

    const question = document.getElementById("question").value;

    chrome.tabs.query(
        {
            active: true,
            currentWindow: true
        },
        function (tabs) {

            const url = tabs[0].url;

            const videoId = new URL(url).searchParams.get("v");

            fetch("http://127.0.0.1:8000/chat", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    video_id: videoId,
                    question: question
                })

            })
            .then(res => res.json())
            .then(data => {

                document.getElementById("answer").innerHTML = data.answer;

            });

        }
    );

});