let data_testing = [];
let index_iter = 0;
let mediaRecorder;
let audioChunks = [];
let recordingTimeout;
let overStatus = false;
let decodedData = atob(qr); 
let questionsArray = JSON.parse(decodedData);
let NAME_USER_GLOBAL = ""

if(document.querySelector('.button_big')){
    let wprTests = document.querySelector('.wpr_tests');
    let preQuestionary = document.querySelector('.pre-questionary')

    $('.button_big').on('click', function() {
        preQuestionary.classList.add('hidden');
        wprTests.classList.remove('hidden');
    });
}


if(document.querySelector('.input_user')){
    if(document.querySelector('.input_user input').value.length <= 2){
        $('#startRecording').attr('disabled', true)
    }else{
        $('#startRecording').attr('disabled', false)
    }
    $('.input_user input').on('input', ()=>{
        if(document.querySelector('.input_user input').value.length <= 2){
            $('#startRecording').attr('disabled', true)
        }else{
            $('#startRecording').attr('disabled', false)
        }
    })
}

navigator.mediaDevices.getUserMedia({ audio: true })
    .then(stream => {
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = event => {
            audioChunks.push(event.data);
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            if(overStatus == false){
                sendData(audioBlob);
            }
            
            audioChunks = [];
        };
    })
    .catch(err => {
        $('#startRecording').remove();
        $("#error").text('In order to start testing you must have a microphone enabled, reload the page and click "Enable"');
    });

function stopRecordingAfterTimeout() {
    clearTimeout(recordingTimeout);
    recordingTimeout = setTimeout(() => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            $("#stopRecording").prop("disabled", true);
            index_iter++;
            startRecord();
        }
    }, 30000);
}

function startRecord() {
    if(document.querySelector('.boxed_info')){
        $('.boxed_info').remove()
    }

    $('.wrapper .content').addClass('loader');
    $('.wrapper .content').css("transition", "1s ease");
    $('.wrapper .content').css("padding-right", "0px");
    $('.boxed_info').css("transition", "1s ease");
    $('.boxed_info').css("right", "-100%");

    $(".q_count #a").text(index_iter)
    $(".q_count #c").text(questionsArray.length)

    setTimeout(() => {
        $("#animation").hide();
        if (questionsArray.length + 1 == index_iter) {
        }else{
            mediaRecorder.start();
        }
        $("#stopRecording").prop("disabled", false);
    }, 2000);

    audioContext = new (window.AudioContext || window.webkitAudioContext)();
    analyser = audioContext.createAnalyser();
    let source = audioContext.createMediaStreamSource(mediaRecorder.stream);
    source.connect(analyser);
    
    analyser.fftSize = 256;
    dataArray = new Uint8Array(analyser.frequencyBinCount);
    try{
        canvas = document.getElementById("visualization");
        canvasContext = canvas.getContext("2d");
        drawVisualization();
    }catch{

    }

    if(index_iter == 1) {
        if(document.querySelector(".slide")){
            const slideContainer = document.querySelector(".slide");
            const currentH3 = slideContainer.querySelector("h3.current") || slideContainer.querySelector("h3");
            currentH3.textContent = questionsArray[0];
    
            setTimeout(() => {
                $('.wrapper .content').remove();
                $('.wrapper .q').removeClass('hidden');
            }, 1000);
        }
    } else {
        if (questionsArray.length + 1 == index_iter) {
            $(".q .question").remove()
            $(".q .load").removeClass("hidden")
            $(".q").addClass("loader")

            if (mediaRecorder && mediaRecorder.state === 'recording') {
                mediaRecorder.stop();
            }
        } else {
            slideText(questiFonsArray[index_iter], questionsArray[index_iter-1]);
        }
    }

    stopRecordingAfterTimeout();
}

$("#startRecording").on("click", function(event) {
    if($('#startRecording').prop('disabled') == false){
        if(document.querySelector('.input_user')){
            NAME_USER_GLOBAL = $('.input_user input').val();
        }

        event.preventDefault();
        index_iter++;
        startRecord();
    }
});

$("#stopRecording").on("click", function(event) {
    event.preventDefault();
    clearTimeout(recordingTimeout);
    mediaRecorder.stop();
    index_iter++;
    startRecord();
});

function sendData(audioBlob) {
    let index_q = index_iter-2;
    console.log(index_q)
    let formData = new FormData();
    formData.append('buffer', audioBlob);
    formData.append('token', 'token');

    fetch('/stream', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        data_testing.push({"question": questionsArray[index_q], "text": data.text})

        if (questionsArray.length + 1 == index_iter) {
            // Finished testing
            if(document.querySelector('#wpr_tests')){
                if($('#wpr_tests').attr('d-type') == "custom"){
                    done_custom()
                }else{
                    done_anonymus()
                }
            }else{
                alert("You have tampered with the element code, we cannot accept the test results from you, we will relaunch the page")
                location.reload()
            }
        }
    })
    .catch(error => {
        alert("An unanticipated error has occurred, please try the test again");
        location.reload()
    });
}

function slideText(currentText, nextText) {
    try {
        const slideContainer = document.querySelector(".slide");
        const currentH3 = slideContainer.querySelector("h3.current") || slideContainer.querySelector("h3");
        currentH3.textContent = currentText;

        const nextH3 = document.createElement("h3");
        nextH3.textContent = nextText;
        nextH3.classList.add("next");
        slideContainer.appendChild(nextH3);

        const currentHeight = currentH3.offsetHeight;
        const nextHeight = nextH3.offsetHeight;

        slideContainer.style.height = `${currentHeight}px`;
        nextH3.style.transform = `translateY(${nextHeight}px)`;

        currentH3.addEventListener('transitionend', function() {
            currentH3.remove();
        }, { once: true });

        nextH3.addEventListener('transitionend', function() {
            nextH3.classList.remove("next");
            nextH3.classList.add("current");
            slideContainer.style.height = "";
        }, { once: true });

        requestAnimationFrame(() => {
            currentH3.style.transform = `translateY(-${currentHeight}px)`;
            nextH3.style.transform = "translateY(0)";
            slideContainer.style.height = `${nextHeight}px`;
        });

        window.addEventListener("resize", function() {
            const slideContainer = document.querySelector(".slide");
            const currentH3 = slideContainer.querySelector("h3.current");
            const nextH3 = slideContainer.querySelector("h3.next");
            
            if (currentH3 && nextH3) {
                const currentHeight = currentH3.offsetHeight;
                const nextHeight = nextH3.offsetHeight;
                
                slideContainer.style.height = nextH3.style.transform === "translateY(0)" ? `${nextHeight}px` : `${currentHeight}px`;
                nextH3.style.transform = nextH3.style.transform === "translateY(0)" ? "translateY(0)" : `translateY(${nextHeight}px)`;
            }
        });
    } catch {

    }
}

function done_screen(){
    setTimeout(()=>{
        $('.thank_you .circle_abs').css('transition', '1s ease')
        $('.thank_you .circle_abs').css('min-width', "5000px")
        $('.thank_you .circle_abs').css('min-height', "5000px")
        $('.thank_you .circle_abs').css('transform', "scale(2)")
        $('.thank_you .circle_abs').css('transform', "scale(2)")
        $('.powered').css('transition', '1s ease')
        $('.powered').css('color', "#fff")
        $('.powered a').css('color', "#000")
    }, 500)
    setTimeout(()=>{
        $('.thank_you .circle_abs').css('transition', '0')
        $('.thank_you .circle_abs').css('min-width', "100%")
        $('.thank_you .circle_abs').css('min-height', "100vh")
        $('.thank_you .circle_abs').css('border-radius', "0")
        $('.content_thankyou').removeClass('hidden')
        $('.content_thankyou .star').html(`<svg viewBox="0 0 846.66 846.66" xmlns="http://www.w3.org/2000/svg" shape-rendering="geometricPrecision" text-rendering="geometricPrecision" image-rendering="optimizeQuality" fill-rule="evenodd" clip-rule="evenodd"><path fill="none" stroke="#ffffff" stroke-width="20" class="path" d="M178.47 417.74c21.61 15.66-2.2 48.52-23.81 32.86L17.28 351.19C.72 339.2 10.51 313.1 30.64 314.53l300.1.57c26.62 0 26.62 40.48 0 40.48l-238.81-.46 86.54 62.62zM383.1 239.09c-8.15 25.37-46.72 12.99-38.58-12.38l59.57-184.53c6.06-18.89 32.77-18.5 38.62.14l88.04 272.75 286.82-.55c19.68 0 27.55 25.25 11.87 36.63l-232.3 168.16 89.15 272.58c6.33 19.49-17.04 34.81-32.44 21.71L423.38 645.48 191.66 814.51c-15.91 11.58-37.12-4.18-31.14-22.6l93.68-286.64c8.25-25.36 46.82-12.83 38.58 12.55l-74.25 227.02 192.61-140.5c6.92-5.27 16.75-5.63 24.14-.25l192.94 140.75-74.02-226.32c-3.04-8.31-.36-17.96 7.15-23.4l193.47-140-237.86.46c-8.92.43-17.38-5.13-20.24-14.04l-73.34-227.23-40.28 124.78z"></path></svg>`)
    }, 1000)
}
if(document.querySelector('#wpr_tests')){
    if($('#wpr_tests').attr('d-app') == "True"){
        done_screen()
    }
}


let count_bad_request = 0;
function done_anonymus(){
    overStatus = true;
    let formData = JSON.stringify({"8v98as99g": data_testing});
    fetch(`/anonymous/done/${to}`, {
        method: 'POST',
        body: formData,
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if(data.success == true){
            $('.wrapper .q').remove()
            $('.thank_you').removeClass('hidden')
            done_screen()
        }else{
            count_bad_request++;
            if(count_bad_request > 5){
                alert("Unfortunately, there was an error with sending the results. Check the connection")
            }else{
                done_anonymus()
            }
        }
    })
    .catch(error => {

    });
}


function done_custom(){
    overStatus = true;
    let dataObject = {"34er456jwqev54": data_testing};
    dataObject.name_user = NAME_USER_GLOBAL;
    let formData = JSON.stringify(dataObject);

    fetch(`/feedback/done/${to}`, {
        method: 'POST',
        body: formData,
        headers: {
            "Content-Type": "application/json",
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        if(data.success == true){
            $('.wrapper .q').remove()
            $('.thank_you').removeClass('hidden')
            done_screen()
        }else{
            count_bad_request++;
            if(count_bad_request > 5){
                alert("Unfortunately, there was an error with sending the results. Check the connection")
            }else{
                done_custom()
            }
        }
    })
    .catch(error => {

    });
}

    
function drawVisualization() {
    try{
        requestAnimationFrame(drawVisualization);
        analyser.getByteFrequencyData(dataArray);
        canvasContext.fillStyle = "#e7e7e7";
        canvasContext.fillRect(0, 0, canvas.width, canvas.height);
    
        let barWidth = (canvas.width / dataArray.length) * 2.5;
        let barHeight;
        let x = 0;
    
        for (let i = 0; i < dataArray.length; i++) {
            barHeight = dataArray[i] / 2;
    
            canvasContext.fillStyle = "#34DD0A";
            canvasContext.fillRect(x, canvas.height - barHeight, barWidth, barHeight);
    
            x += barWidth + 1;
        }
    }catch{

    }
}
